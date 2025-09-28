import { createSlice, type PayloadAction } from "@reduxjs/toolkit"
import type { Config } from "./types"

const initialState: Config = { }

const configSlice = createSlice({
  name: "config",
  initialState,
  reducers: {
    updateConfig: (state, action: PayloadAction<Config | undefined>) => {
      if (action.payload) {
        state = {...state, ...action.payload}
      } else {
        state = {...initialState}
      }
    },
  }
})

export const configActions = configSlice.actions

export default configSlice.reducer