import { createSlice, type PayloadAction } from "@reduxjs/toolkit"
import type { Config } from "./types"

const initialState: Config = {
  config_file: "",
  destination: "",
  source: "",
  tmdb_token: "",
  makemkvcon_path: "",
  log_level: "ERROR",
  log_file: "",
  temp_prefix: "",
  frontend: "",
  listen_port: "",
  cors_origins: [],
  ui_path: ""
}

const configSlice = createSlice({
  name: "config",
  initialState,
  reducers: {
    updateConfig: (state, action: PayloadAction<Partial<Config>>) => ({
      ...state, ...action.payload
    }),
  }
})

export const configActions = configSlice.actions

export default configSlice