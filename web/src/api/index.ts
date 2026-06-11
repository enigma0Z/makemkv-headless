import { configureStore, type Middleware, type UnknownAction } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";

import rip, { ripActions, type RipState } from './v1/rip/store'
import socket, { type SocketState } from "./v1/socket/store";
import { SOCKET_URI, SocketConnection } from "./v1/socket/api";
import { setupListeners } from "@reduxjs/toolkit/query";
import { stateApi } from "./v1/state/api";
import { api as apiV1 } from "./v1";
import type { Config } from "./v1/config/types";
import config, { configActions } from './v1/config/store'
import { configApi } from "./v1/config/api";
import { throttle } from "lodash";

export interface RootState {
  config: Config,
  rip: RipState,
  socket: SocketState
}

// Exploded currying syntax, for reference
// const updateApiMiddleware: Middleware<{}, RootState> = (store) => {
//   return function wrapDispatch(next) { // next
//     return function updateApi(action) { // action
//       // Do things with store, next, action
//     }
//   }
// }

const API_THROTTLE_RATE = 1000

const throttledApiUpdate = {
  config: throttle((callback: () => void) => callback(), API_THROTTLE_RATE),
  rip: throttle((callback: () => void) => callback(), API_THROTTLE_RATE)
}

const updateApiMiddleware: Middleware<{}, RootState> = store => next => _action => {
  const action = (_action as any) // Make TS happy

  if (action.type === 'api/executeQuery/fulfilled') {
    if (action.meta?.arg?.endpointName === 'getState') {
      console.log('Update rip store from API', action.payload.rip)
      store.dispatch(ripActions.setRipData(action.payload.rip))
    } else if (action.meta?.arg?.endpointName === 'getConfig') {
      console.log('Update config store from API', action.payload)
      store.dispatch(configActions.updateConfig(action.payload))
    }
  }

  if (action.type.startsWith('rip/')) {
    const currentRipState = store.getState().rip
    const result = next(action)
    const nextRipState = store.getState().rip
    if (JSON.stringify(currentRipState) !== JSON.stringify(nextRipState)) {
      throttledApiUpdate.rip(() => {
        console.log('Put rip state API', currentRipState, nextRipState)
        const initiate: UnknownAction = (stateApi.endpoints.putState.initiate({ rip: nextRipState }) as any)
        store.dispatch(initiate)
      })
    }
    return result
  } else if (action.type == 'config/updateConfig') {
    const currentConfigState = store.getState().config
    const result = next(action)
    const nextConfigState = store.getState().config
    if (JSON.stringify(currentConfigState) !== JSON.stringify(nextConfigState)) {
      throttledApiUpdate.config(() => {
        console.log('Put config into API', currentConfigState, nextConfigState)
        const initiate: UnknownAction = (configApi.endpoints.putConfig.initiate(nextConfigState) as any)
        store.dispatch(initiate)
      })
    }
    return result
  }

  return next(action)
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
    rip: rip.reducer, config: config.reducer, socket, api: apiV1.reducer
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


