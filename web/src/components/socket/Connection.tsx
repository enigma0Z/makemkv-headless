import { useEffect } from "react"
import { socket } from "."
import endpoints from "@/api/endpoints"
import type { ApiState } from "@/api/types/status"
import { store } from "@/api/store"
import { socketActions, type SocketState } from "@/api/store/socket"
import { throttle } from "lodash"

const RECONNECT_DELAY_MS = 1000

export function isRippingStatus(status: string | undefined) {
  return (
    status === "Analyzing seamless segments"
    || status === "Saving to MKV file"
  )
}

export function isCompleteEnough(progress: number | null | undefined) {
  return (progress ?? 0) > .999
}

const throttledUpdateSocketState = throttle(
  (newState: SocketState['ripState']) => {
    console.info('Throttled update socket state')
    store.dispatch(socketActions.updateSocketState(newState))
  }, 
  500
  // { trailing: true, leading: true }
)

const shouldUpdateProgress = (current: number | undefined | null, next: number, logName: string = "") => {
  if (current === undefined || current === null) {
    console.debug('Do update (undefined)', logName)
    return true
  } else if (next - current > 0.001) {
    console.debug('Do update', next - current, logName)
    return true
  }

  console.debug('Skip update', logName)
  return false
}

const SocketConnection = () => {
  const setupHandlers = () => {
    socket.on("connect", () => {
      console.info("Socket connected")
      store.dispatch(socketActions.updateSocketState({ connected: true }))
    })

    // Reconnect on disconnect
    socket.on("connect_error", () => {
      console.error("Could not connect to socket")
      store.dispatch(socketActions.updateSocketState({ connected: false }))
      setTimeout(() => socket.connect(), RECONNECT_DELAY_MS)
    })

    socket.on("disconnect", () => {
      console.info("Socket disconnected")
      store.dispatch(socketActions.updateSocketState({ connected: false }))
      setTimeout(() => socket.connect(), RECONNECT_DELAY_MS)
    })

    socket.on("MessageEvent", (value) => {
      if (value.text.startsWith("Copy complete")) {
        store.dispatch(socketActions.updateSocketState({
          rip_started: false,
          current_status: undefined
        }))
      }

      store.dispatch(socketActions.appendToMessages(value))
    })

    socket.on("ProgressMessageEvent", (value) => {
      // Set index if current index is undefined
      const socketState = store.getState().socket.ripState
      const nextSocketState: SocketState['ripState'] = { 
        ...socketState, 
        current_progress: [ ...(socketState.current_progress ?? []) ]
      }

      if (value.progress_type === "current" && socketState.current_title !== null && socketState.current_title !== undefined) {
        if (
          socketState.rip_started
          && isRippingStatus(socketState.current_status)
          && (
            socketState.current_title === undefined 
            || socketState.current_title === null
            || value.index > socketState.current_title
          )
        ) {
          console.info('Starting next title')
          nextSocketState.current_title = value.index
        } 

        nextSocketState.current_status = value.name

        if ( // We have advanced to the next title
          nextSocketState.current_progress !== undefined
          && socketState.current_title !== undefined 
          && nextSocketState.current_title !== undefined
          && nextSocketState.current_title !== null
          && socketState.current_title < nextSocketState.current_title
        ) {
          nextSocketState.current_progress[socketState.current_title] = {buffer: 1, progress: 1}
        }
      } else if (value.progress_type === "total") {
        nextSocketState.total_status = value.name

        if (value.name === "Saving all titles to MKV files") {
          nextSocketState.rip_started = true
        }
      }

      store.dispatch(socketActions.updateSocketState(nextSocketState))
    })

    socket.on("ProgressValueMessageEvent", (value) => {
      const socketState = store.getState().socket.ripState
      const nextSocketState: SocketState['ripState'] = {
        current_progress: socketState.current_progress?.slice(),
        total_progress: { ... socketState.total_progress }
      }

      // Set progress value for current index
      if (socketState.current_title !== undefined && socketState.current_title !== null) {
        if (nextSocketState.current_progress === undefined) {
          nextSocketState.current_progress = []; 
        }

        if (nextSocketState.current_progress[socketState.current_title] === undefined) {
          nextSocketState.current_progress[socketState.current_title] = {progress: 0, buffer: undefined}
        }
        
        if (socketState.current_status === "Analyzing seamless segments") {
          nextSocketState.current_progress[socketState.current_title] = {
            buffer: value.current / value.max
          }
        } else if (socketState.current_status === "Saving to MKV file") {
          nextSocketState.current_progress[socketState.current_title] = {
            buffer: 1,
            progress: value.current / value.max
          }
        }
      } 

      if (nextSocketState.total_progress === undefined) {
        nextSocketState.total_progress = {progress: 0, buffer: 0}
      }

      if (socketState.rip_started) {
        nextSocketState.total_progress = {
          buffer: 1,
          progress: value.total / value.max
        }
      } else {
        nextSocketState.total_progress = {
          buffer: value.total / value.max
        }
      }

      throttledUpdateSocketState(nextSocketState)
    })
    
    socket.on("RipStartStopMessageEvent", (value) => {
      const socketState = store.getState().socket.ripState
      const nextSocketState: SocketState['ripState'] = { }

      nextSocketState.rip_started = value.state === "start"

      if (value.index !== null) {
        nextSocketState.current_title = value.index
      }

      if ( // We have advanced to the nextSocketState title
        nextSocketState.current_progress
        && socketState.current_title !== null
        && socketState.current_title !== undefined 
        && nextSocketState.current_title !== null
        && nextSocketState.current_title !== undefined
        && socketState.current_title < nextSocketState.current_title
      ) {
        nextSocketState.current_progress[socketState.current_title] = {buffer: 1, progress: 1}
      }

      store.dispatch(socketActions.updateSocketState(nextSocketState))
    })
  }

  useEffect(() => {
    // Initialize socket state
    fetch(endpoints.state.get("socket"), { method: 'GET' })
      .then(response => response.json() as Promise<ApiState>)
      .then((json) => {
        store.dispatch(socketActions.updateSocketState(json.socket)) // Socket context
      })

    // Set up socket connection
    setupHandlers()
    socket.connect()

    return () => {
      socket.off("MessageEvent")
      socket.off("ProgressMessageEvent")
      socket.off("ProgressValueMessageEvent")
      socket.disconnect()
      store.dispatch(socketActions.updateSocketState({ connected: false }))
    }
  }, [])

  return <></>
}

export default SocketConnection