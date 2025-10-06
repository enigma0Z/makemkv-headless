import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Toc } from "./types";

const initialState: Partial<Toc> = {
  lines: [],
  source: undefined,
  loading: false
}

const tocSlice = createSlice({
  name: "toc",
  initialState,
  reducers: {
    setTocData: (state, action: PayloadAction<Toc | undefined>) => {
      if (action.payload) {
        state.lines = action.payload.lines
        state.source = action.payload.source
      } else {
        state.lines = []
        state.source = undefined
      }
    },
    setTocLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    }
  }
})

export const tocActions = tocSlice.actions

export default tocSlice.reducer