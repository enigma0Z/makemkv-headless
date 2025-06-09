import { configureStore } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";

import rip from './rip'

export const store = configureStore({
  reducer: {
    rip
  }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()

export type ValidationEntry<T, S> = Record<string, (value: T, state?: S) => boolean>

export type StateValidationEntryTypes<T> = (
  ValidationEntry<string, T> |
  ValidationEntry<number, T>
)
export type StateValidation<T> = { [key: string]: StateValidationEntryTypes<T> | StateValidation<T> }