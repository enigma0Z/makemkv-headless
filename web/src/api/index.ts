import { configureStore, type Middleware, type UnknownAction } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";

import rip, { ripActions, type RipState } from './v1/rip/store'
import socket, { type SocketState } from "./v1/socket/store";
import { SOCKET_URI, SocketConnection } from "./v1/socket/api";
import { setupListeners } from "@reduxjs/toolkit/query";
import { stateApi } from "./v1/state/api";
import { api as apiV1 } from "./v1";

export type RootState = {
  rip: RipState,
  socket: SocketState
}

const updateApiMiddleware: Middleware<{}, RootState> = store => next => _action => {
  const action = (_action as any)
  if (action.type === 'api/executeQuery/fulfilled') {
    if (action.meta?.arg?.endpointName === 'getState') {
      console.log('Update rip state from API', action.payload.rip)
      store.dispatch(ripActions.setRipData(action.payload.rip))
    }
  }
  
  if ((action as UnknownAction).type.startsWith('rip/')) {
    const currentRipState = store.getState().rip
    const result = next(action)
    const nextRipState = store.getState().rip
    if (JSON.stringify(currentRipState) !== JSON.stringify(nextRipState)) {
      console.log('Put state into API', currentRipState, nextRipState)
      const initiate: UnknownAction = (stateApi.endpoints.putState.initiate({ rip: nextRipState }) as any)
      store.dispatch(initiate)
    }
    return result
  }

  return next(action)
}

export type ThunkExtraArgument = {
  socketConnection: SocketConnection
}

export const store = configureStore({
  middleware: (getDefaultMiddleware) => getDefaultMiddleware({
    thunk: {
      extraArgument: {
        socketConnection: new SocketConnection(SOCKET_URI)
      }
    }
  }).concat(
    updateApiMiddleware
  ).concat(
    apiV1.middleware
  ),
  reducer: {
    rip: rip.reducer, socket, api: apiV1.reducer
  },
})

setupListeners(store.dispatch)

export type AppDispatch = typeof store.dispatch

export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()

export type ValidationEntry<T, S> = Record<string, (value: T, state?: S) => boolean>

export type StateValidationEntryTypes<T> = (
  ValidationEntry<string, T> |
  ValidationEntry<number, T> |
  ValidationEntry<boolean, T>
)

export type StateValidation<T> = { [key: string]: (StateValidationEntryTypes<T> | StateValidation<T>) }


