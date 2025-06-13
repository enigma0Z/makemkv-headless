import { useContext, useEffect } from "react"
import { Context, type SetStateCallback } from "./Context"
import { socket } from "."

const RECONNECT_DELAY_MS = 1000

function appendToEventQueue<T>(
  callback: SetStateCallback<T[] | undefined> | undefined,
  value: T
): void {
  callback && callback((prev) => prev ? [...prev, value] : [value])
}

const SocketConnection = () => {
  const {
    setConnected,
    setMessageEvents,
    setProgressMessageEvents,
    setProgressValueMessageEvents,
    setRipStartStopMessageEvents,
    setRipState
  } = useContext(Context)

  const connect = () => {
    socket.connect()
  }

  const setupHandlers = () => {
    socket.on("connect", () => {
      console.log("Socket connected")
      setConnected(true)
    })

    // Reconnect on disconnect
    socket.on("connect_error", () => {
      console.error("Could not connect to socket")
      setConnected(false)
      setTimeout(() => socket.connect(), RECONNECT_DELAY_MS)
    })

    socket.on("disconnect", () => {
      console.info("Socket disconnected")
      setConnected(false)
      setTimeout(() => socket.connect(), RECONNECT_DELAY_MS)
    })

    socket.on("MessageEvent", (value) => {
      if (value.text.startsWith("Copy complete")) {
        setRipState && setRipState((prev) => {
          const next = {...prev}
          next.ripStarted = false
          next.currentStatus = undefined
          return next
        })
      }
      appendToEventQueue<typeof value>(setMessageEvents, value)
    })

    socket.on("ProgressMessageEvent", (value) => {
      // Set index if current index is undefined
      console.log('ProgressMessageEvent', setRipState, value)
      if (value.progressType === "Current") {
        setRipState && setRipState((prev) => {
          const next = {...prev}
          if (
            next.ripStarted 
            && (
              next.currentTitle === undefined 
              || value.index > next.currentTitle
            )
          ) {
            next.currentTitle = value.index
          }

          next.currentStatus = value.name

          if ( // We have advanced to the next title
            next.currentProgress
            && prev?.currentTitle !== undefined 
            && next?.currentTitle !== undefined
            && prev.currentTitle < next.currentTitle
          ) {
            next.currentProgress[prev.currentTitle] = {buffer: 100, progress: 100}
          }

          console.log('Updating current status, index', next)
          return next
        });
      } else if (value.progressType === "Total") {
        setRipState && setRipState((prev) => {
          const next = {...prev}
          next.totalStatus = value.name

          if (value.name === "Saving all titles to MKV files") {
            next.ripStarted = true
          }

          return next
        });
      }

      // Set status message(s)
      appendToEventQueue<typeof value>(setProgressMessageEvents, value)
    })

    socket.on("ProgressValueMessageEvent", (value) => {
      // Set progress value for current index
      console.log('ProgressValueEvent', value, setRipState)
      setRipState && setRipState((prev) => {
        const next = {...prev}
        if (next.currentTitle !== undefined) {
          if (next.currentProgress === undefined) next.currentProgress = []; 
          if (next.currentProgress[next.currentTitle] === undefined) {
            next.currentProgress[next.currentTitle] = {progress: 0, buffer: undefined}
          }
          
          if (next.currentStatus === "Analyzing seamless segments") {
            next.currentProgress[next.currentTitle].buffer = value.current / value.max * 100
          } else if (next.currentStatus === "Saving to MKV file") {
            next.currentProgress[next.currentTitle].buffer = 100
            next.currentProgress[next.currentTitle].progress = value.current / value.max * 100
          }
        }

        if (next.totalProgress === undefined) {
          next.totalProgress = {progress: 0, buffer: 0}
        }

        if (next.ripStarted) {
          next.totalProgress.progress = value.total / value.max * 100
        } else {
          next.totalProgress.buffer = value.total / value.max * 100
        }
        return next
      })
      // Set progress value for total
      appendToEventQueue<typeof value>(setProgressValueMessageEvents, value)
    })
    
    socket.on("RipStartStopMessageEvent", (value) => {
      console.log("RipStartMessageEvent", value)
      setRipState && setRipState((prev) => {
        const next = {...prev};
        if (value.index) {
          next.currentTitle = value.index
        }

        if ( // We have advanced to the next title
          next.currentProgress
          && prev?.currentTitle !== undefined 
          && next?.currentTitle !== undefined
          && prev.currentTitle < next.currentTitle
        ) {
          next.currentProgress[prev.currentTitle] = {buffer: 100, progress: 100}
        }

        return next
      });

      // Set index if > than current index or current index is undefined
      appendToEventQueue<typeof value>(setRipStartStopMessageEvents, value)
    })
  }

  useEffect(() => {
    setupHandlers()
    connect()

    return () => {
      socket.off("MessageEvent")
      socket.off("ProgressMessageEvent")
      socket.off("ProgressValueMessageEvent")
      socket.disconnect()
      setConnected(false)
    }
  }, [])

  return <></>
}

export default SocketConnection