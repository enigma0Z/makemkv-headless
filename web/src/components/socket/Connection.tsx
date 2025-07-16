import { useContext, useEffect } from "react"
import { Context, type SetStateCallback } from "./Context"
import { socket } from "."
import endpoints from "@/api/endpoints"
import type { ApiState } from "@/api/types/status"

const RECONNECT_DELAY_MS = 1000

function isRippingStatus(status: string | undefined) {
  return (
    status === "Analyzing seamless segments"
    || status === "Saving to MKV file"
  )
}

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
    ripState,
    setRipState
  } = useContext(Context)

  const setupHandlers = () => {
    socket.on("connect", () => {
      console.info("Socket connected")
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
          next.rip_started = false
          next.current_status = undefined
          return next
        })
      }
      appendToEventQueue<typeof value>(setMessageEvents, value)
    })

    socket.on("ProgressMessageEvent", (value) => {
      // Set index if current index is undefined
      if (value.progress_type === "current") {
        setRipState && setRipState((prev) => {
          const next = {...prev}
          if (
            next.rip_started 
            && isRippingStatus(next.current_status)
            && (
              next.current_title === undefined 
              || value.index > next.current_title
            )
          ) {
            next.current_title = value.index
          }

          next.current_status = value.name

          if ( // We have advanced to the next title
            next.current_progress
            && prev?.current_title !== undefined 
            && next?.current_title !== undefined
            && prev.current_title < next.current_title
          ) {
            next.current_progress[prev.current_title] = {buffer: 1, progress: 1}
          }

          return next
        });
      } else if (value.progress_type === "total") {
        setRipState && setRipState((prev) => {
          const next = {...prev}
          next.total_status = value.name

          if (value.name === "Saving all titles to MKV files") {
            next.rip_started = true
          }

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
        if (next.current_title !== undefined) {
          if (next.current_progress === undefined) next.current_progress = []; 
          if (next.current_progress[next.current_title] === undefined) {
            next.current_progress[next.current_title] = {progress: 0, buffer: undefined}
          }
          
          if (next.current_status === "Analyzing seamless segments") {
            next.current_progress[next.current_title].buffer = value.current / value.max
          } else if (next.current_status === "Saving to MKV file") {
            next.current_progress[next.current_title].buffer = 1
            next.current_progress[next.current_title].progress = value.current / value.max
          }
        }

        if (next.total_progress === undefined) {
          next.total_progress = {progress: 0, buffer: 0}
        }

        if (next.rip_started) {
          next.total_progress.buffer = 1
          next.total_progress.progress = value.total / value.max
        } else {
          next.total_progress.buffer = value.total / value.max
        }
        return next
      })
      // Set progress value for total
      appendToEventQueue<typeof value>(setProgressValueMessageEvents, value)
    })
    
    socket.on("RipStartStopMessageEvent", (value) => {
      setRipState && setRipState((prev) => {
        const next = {...prev};

        next.rip_started = value.state === "start"

        if (value.index) {
          next.current_title = value.index
        }

        if ( // We have advanced to the next title
          next.current_progress
          && prev?.current_title !== undefined 
          && next?.current_title !== undefined
          && prev.current_title < next.current_title
        ) {
          next.current_progress[prev.current_title] = {buffer: 1, progress: 1}
        }

        return next
      });

      // Set index if > than current index or current index is undefined
      appendToEventQueue<typeof value>(setRipStartStopMessageEvents, value)
    })
  }

  useEffect(() => {
    // Initialize socket state
    fetch(endpoints.state.get("socket"), { method: 'GET' })
      .then(response => response.json() as Promise<ApiState>)
      .then((json) => {
        setRipState && setRipState(json.socket) // Socket context
      })

    // Set up socket connection
    setupHandlers()
    socket.connect()

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