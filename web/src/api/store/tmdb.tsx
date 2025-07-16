import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type TmdbConfiguration = {
  change_keys: string[];
  images: {
    base_url: string;
    secure_base_url: string;
    backdrop_sizes: string[];
    logo_sizes: string[];
    poster_sizes: string[];
    profile_sizes: string[];
    still_sizes: string[];
  }
}

export type TmdbState = {
  configuration?: TmdbConfiguration
}

const initialState: TmdbState = {
  configuration: undefined,
}

const tmdbSlice = createSlice({
  name: "tmdb",
  initialState,
  reducers: {
    setTmdbConfiguration: (state, action: PayloadAction<TmdbConfiguration | undefined>) => {
      if (action.payload) {
        state.configuration = action.payload
      } else {
        state.configuration = undefined
      }
    }
  }
})

export const tmdbActions = tmdbSlice.actions

export default tmdbSlice.reducer