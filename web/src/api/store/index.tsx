import { configureStore } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";

import rip, { ripStateIsValid } from './rip'
import toc from './toc'
import endpoints from "../endpoints";

export const store = configureStore({
  reducer: {
    rip, toc
  }
})

export type RootState = ReturnType<typeof store.getState>
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

store.subscribe(() => {
  const { rip } = store.getState()
  if (ripStateIsValid(rip)) {
    fetch(endpoints.state(), { method: 'PUT', body: JSON.stringify({
      redux: { rip }
    })})
  }
})