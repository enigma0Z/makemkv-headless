import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { ShowInfo, SortInfo } from "../sort/types";
import { uniqueFilter } from "@/util/array";
import type { TmdbSearchResult } from "../tmdb/types";

export interface RipState {
  destination: RipStateDestination;
  sort_info: SortInfo & ShowInfo;
  toc_length: number
  tmdb_selection: TmdbSearchResult | null
}

interface RipStateDestination {
    library?: string;
    media?: string;
    content?: string;
}

const initialState: RipState = {
  destination: {
    library: undefined,
    media: undefined,
    content: undefined
  },
  sort_info: {
    name: undefined,
    id: undefined,
    first_episode: undefined,
    season_number: undefined,
    main_indexes: [],
    extra_indexes: [],
    split_segments: undefined,
    id_db: 'tmdbid'
  },
  toc_length: 0,
  tmdb_selection: null
}

export const ripStateIsValid = (state: RipState) => (
  state.destination?.library !== undefined
  && state.destination.media !== undefined
  && state.destination.content !== undefined
  && state.sort_info.name !== undefined
  && state.sort_info.id !== undefined
)

const ripSlice = createSlice({
  name: "rip",
  initialState,
  reducers: {
    setRipData: (state, action: PayloadAction<RipState | undefined>) => {
      console.debug('setRipData', action.payload)
      if (action.payload) {
        console.debug('applying')
        state.destination = action.payload.destination ?? initialState.destination
        state.sort_info = action.payload.sort_info ?? initialState.sort_info
        state.toc_length = action.payload.toc_length ?? initialState.toc_length
        state.tmdb_selection = action.payload.tmdb_selection ?? initialState.tmdb_selection
      }
    },
    updateSortInfo: (state, action: PayloadAction<RipState['sort_info']>) => {
      state.sort_info = {...state.sort_info, ...action.payload}
    },
    setLibrary: (state, action: PayloadAction<RipStateDestination['library']>) => {
      state.destination = {...state.destination, library: action.payload}
    },
    setMedia: (state, action: PayloadAction<RipStateDestination['media']>) => {
      state.destination = {...state.destination, media: action.payload}
    },
    setContent: (state, action: PayloadAction<RipStateDestination['content']>) => {
      state.destination = {...state.destination, content: action.payload}
    },
    setMainIndexes: (state, action: PayloadAction<number[]>) => {
      state.sort_info.main_indexes = action.payload
    },
    setExtraIndexes: (state, action: PayloadAction<number[]>) => {
      state.sort_info.extra_indexes = action.payload
    },
    addMainIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.main_indexes.push(action.payload)
      state.sort_info.main_indexes.sort()
      state.sort_info.main_indexes = state.sort_info.main_indexes.filter(uniqueFilter)
    },
    addExtraIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.extra_indexes.push(action.payload)
      state.sort_info.extra_indexes.sort()
      state.sort_info.extra_indexes = state.sort_info.extra_indexes.filter(uniqueFilter)
    },
    removeMainIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.main_indexes = state.sort_info.main_indexes.filter((value) => value !== action.payload)
    },
    swapMainIndexForward: (state, action: PayloadAction<number>) => {
      const indexOfIndex = state.sort_info.main_indexes.indexOf(action.payload)

      // Make sure we are not swapping the last element off the end of the array
      if (
        indexOfIndex + 1 < state.sort_info.main_indexes.length
        && indexOfIndex > -1
      ) {
        state.sort_info.main_indexes = [
          ...state.sort_info.main_indexes.slice(0, indexOfIndex),
          state.sort_info.main_indexes[indexOfIndex+1],
          state.sort_info.main_indexes[indexOfIndex],
          ...state.sort_info.main_indexes.slice(indexOfIndex+2)
        ]
      }
    },
    swapMainIndexBackward: (state, action: PayloadAction<number>) => {
      const indexOfIndex = state.sort_info.main_indexes.indexOf(action.payload)

      // Make sure we are not swapping the last element off the end of the array
      if (
        indexOfIndex > 0
        && indexOfIndex < state.sort_info.main_indexes.length
      ) {
        state.sort_info.main_indexes = [
          ...state.sort_info.main_indexes.slice(0,indexOfIndex-1), 
          state.sort_info.main_indexes[indexOfIndex], 
          state.sort_info.main_indexes[indexOfIndex-1], 
          ...state.sort_info.main_indexes.slice(indexOfIndex+1)
        ]
      }
    },
    removeExtraIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.extra_indexes = state.sort_info.extra_indexes.filter((value) => value !== action.payload)
    },
    setTocLength: (state, action: PayloadAction<number | undefined>) => {
      state.toc_length = action.payload ?? 0
    },
    setName: (state, action: PayloadAction<string>) => {
      state.sort_info.name = action.payload
    },
    setId: (state, action: PayloadAction<string>) => {
      state.sort_info.id = action.payload
    },
    setFirstEpisode: (state, action: PayloadAction<number | undefined>) => {
      state.sort_info.first_episode = action.payload
    },
    setSeasonNumber: (state, action: PayloadAction<number | undefined>) => {
      state.sort_info.season_number = action.payload
    },
    setSplitSegments: (state, action: PayloadAction<number[] | undefined>) => {
      state.sort_info.split_segments = action.payload
    },
    setTmdbSelection: (state, action: PayloadAction<TmdbSearchResult>) => {
      state.tmdb_selection = action.payload
    }
  }
})

export const ripActions = ripSlice.actions

export default ripSlice