import { type RootState, type ThunkExtraArgument } from "@/api";
import type { UnknownAction } from "@reduxjs/toolkit";
import type { ThunkAction } from "redux-thunk";
import { socketActions, type SocketState } from "./store";
import { isRippingStatus, type LogMessage, type MkvLogMessage, type ProgressMessage, type ProgressValueMessage, type RipStartStopMessage, type TocStatusMessage } from "@/api/v1/socket/model";
import { endpoints, type ApiModel } from "@/api/endpoints";
import { tocActions } from "../toc/store";
import { throttle } from "lodash";

type SocketThunkAction<T> = ThunkAction<T, RootState, ThunkExtraArgument, UnknownAction>

export const socketConnect = (): SocketThunkAction<void> => (
  dispatch, getState, { socketConnection }
) => {
  const throttledUpdateSocketState = throttle(
    (newState: SocketState['ripState']) => {
      console.info('Throttled update socket state')
      dispatch(socketActions.updateSocketState(newState))
    },
    500
    // { trailing: true, leading: true }
  )

  socketConnection.on("LogMessage", (value: LogMessage) => {
    if (value.message.startsWith("Copy complete")) {
      dispatch(socketActions.updateSocketState({
        rip_started: false,
        current_status: undefined
      }))
    }

    dispatch(socketActions.appendToMessages(value.message))
  })

  socketConnection.on("MkvLogMessage", (value: MkvLogMessage) => {
    if (value.text.startsWith("Copy complete")) {
      dispatch(socketActions.updateSocketState({
        rip_started: false,
        current_status: undefined
      }))
    }

    dispatch(socketActions.appendToMessages(value.text))
  })

  socketConnection.on("TocStatusMessage", (value: TocStatusMessage) => {
    if (value.state === "complete") {
      fetch(endpoints.state.get("redux/toc"), { method: 'GET' })
        .then(response => response.json() as Promise<ApiModel['v1']['state']>)
        .then(({ data }) => {
          if (data.redux?.toc) {
            dispatch(tocActions.setTocData(data.redux.toc))
            dispatch(tocActions.setTocLoading(false))
          }
        })
    }
  })

  const progressMessageHandler = (value: ProgressMessage) => {
    // Set index if current index is undefined
    console.debug('ProgressMessage', value)
    const socketState = getState().socket.ripState
    const nextSocketState: SocketState['ripState'] = {
      ...socketState,
      current_progress: [...(socketState.current_progress ?? [])]
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
        nextSocketState.current_progress[socketState.current_title] = { buffer: 1, progress: 1 }
      }
    } else if (value.progress_type === "total") {
      nextSocketState.total_status = value.name

      if (value.name === "Saving all titles to MKV files") {
        nextSocketState.rip_started = true
      }
    }

    dispatch(socketActions.updateSocketState(nextSocketState))
  }

  socketConnection.on("CurrentProgressMessage", progressMessageHandler)
  socketConnection.on("TotalProgressMessage", progressMessageHandler)

  socketConnection.on("ProgressValueMessage", (value: ProgressValueMessage) => {
    // console.debug('ProgressValueMessage', value)
    const socketState = getState().socket.ripState
    const nextSocketState: SocketState['ripState'] = {
      current_progress: socketState.current_progress?.slice(),
      total_progress: { ...socketState.total_progress }
    }

    // Set progress value for current index
    if (socketState.current_title !== undefined && socketState.current_title !== null) {
      if (nextSocketState.current_progress === undefined) {
        nextSocketState.current_progress = [];
      }

      if (nextSocketState.current_progress[socketState.current_title] === undefined) {
        nextSocketState.current_progress[socketState.current_title] = { progress: 0, buffer: undefined }
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
      nextSocketState.total_progress = { progress: 0, buffer: 0 }
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

  socketConnection.on("RipStartStopMessage", (value: RipStartStopMessage) => {
    const socketState = getState().socket.ripState
    const nextSocketState: SocketState['ripState'] = {}

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
      nextSocketState.current_progress[socketState.current_title] = { buffer: 1, progress: 1 }
    }

    dispatch(socketActions.updateSocketState(nextSocketState))
  })

  socketConnection.connect()
}
