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
    setRipStartMessageEvents,
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
      console.error("Socket disconnected")
      setConnected(false)
      setTimeout(() => socket.connect(), RECONNECT_DELAY_MS)
    })

    socket.on("MessageEvent", (value) =>
      appendToEventQueue<typeof value>(setMessageEvents, value)
    )

    socket.on("ProgressMessageEvent", (value) => {
      // Set index if current index is undefined
      if (value.progressType === "Current") {
        setRipState && setRipState((prev) => {
          const next = {...prev}
          if (next.currentTitle === undefined || value.index > next.currentTitle) {
            next.currentTitle = value.index
          }

          next.currentStatus = value.name
          return next
        });
      } else if (value.progressType === "Total") {
        setRipState && setRipState((prev) => {
          const next = {...prev}
          next.totalStatus = value.name
          return next
        });
      }

      // Set status message(s)
      appendToEventQueue<typeof value>(setProgressMessageEvents, value)
    })

    socket.on("ProgressValueMessageEvent", (value) => {
      // Set progress value for current index
      setRipState && setRipState((prev) => {
        const next = {...prev}
        if (next.currentProgress && next.currentTitle) {
          if (next.currentStatus === "Analyzing seamless segments")
            next.currentProgress[next.currentTitle].buffer = value.current / value.max
          else if (next.currentStatus === "Saving to MKV file")
            next.currentProgress[next.currentTitle].progress = value.current / value.max
        }
        return next
      })
      // Set progress value for total
      appendToEventQueue<typeof value>(setProgressValueMessageEvents, value)
    })
    
    socket.on("RipStartMessageEvent", (value) => {
      console.log("RipStartMessageEvent", value)
      // Set index if > than current index or current index is undefined
      appendToEventQueue<typeof value>(setRipStartMessageEvents, value)
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