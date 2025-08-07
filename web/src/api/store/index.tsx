import { configureStore, type Middleware, type UnknownAction } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";
import { throttle } from "lodash";

import rip, { ripStateIsValid, type RipState } from './rip'
import toc, { type TocState } from './toc'
import tmdb, { type TmdbState } from "./tmdb";
import socket, { type SocketState } from "./socket";
import { endpoints } from "../endpoints";

export type RootState = {
  rip: RipState,
  toc: TocState,
  tmdb: TmdbState,
  socket: SocketState
}

const updateRipStateOnApi = throttle(async (ripState: RipState) => {
  if (ripStateIsValid(ripState)) {
    console.info("Updating rip state on API")
    fetch(endpoints.state.get(), { method: 'PUT', headers: { 'content-type': 'application/json' }, body: JSON.stringify({
      redux: { rip: ripState }
    })})
  } else {
    console.info("Cannot update rip state, is not valid", ripState)
  }
}, 500, {leading: false, trailing: true})

const updateApiMiddleware: Middleware<{}, RootState> = store => next => action => {
  if ((action as UnknownAction).type.startsWith('rip/')) {
    const result = next(action)
    const nextRipState = store.getState().rip
    updateRipStateOnApi(nextRipState)
    
    return result
  } else {
    return next(action)
  }
}

export const store = configureStore({
  middleware: (getDefaultMiddleware) => getDefaultMiddleware()
    .concat(updateApiMiddleware),
  reducer: {
    rip, toc, tmdb, socket
  }
})

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


