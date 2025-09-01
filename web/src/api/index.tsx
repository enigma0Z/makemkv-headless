import { configureStore, type Middleware, type UnknownAction } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";
import { throttle } from "lodash";

import rip, { ripStateIsValid, type RipState } from './v1/rip/store'
import toc, { type TocState } from './v1/toc/store'
import tmdb, { type TmdbState } from "./v1/tmdb/store";
import socket, { type SocketState } from "./v1/socket/store";
import { BACKEND, endpoints } from "./endpoints";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

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

export const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: BACKEND }),
  endpoints: () => ({}),
})

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
    .concat(updateApiMiddleware)
    .concat(api.middleware),
  reducer: {
    rip, toc, tmdb, socket, api: api.reducer
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


