import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { ShowInfo, SortInfo } from "../types/SortInfo";
import { uniqueFilter } from "@/util/array";

export interface RipState {
  destination: RipStateDestination;
  rip_all: boolean;
  sort_info: SortInfo & ShowInfo;
  toc_length?: number
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
  rip_all: false,
  toc_length: 0
}

export const ripStateIsValid = (state: RipState) => (
  state.destination.library !== undefined
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
      console.debug('setRipData', action)
      if (action.payload) {
        state.destination = action.payload.destination
        state.rip_all = action.payload.rip_all
        state.sort_info = action.payload.sort_info
        state.toc_length = action.payload.toc_length
      }
    },
    updateSortInfo: (state, action: PayloadAction<RipState['sort_info']>) => {
      state.sort_info = {...state.sort_info, ...action.payload}
    },
    setRipAll: (state, action: PayloadAction<RipState['rip_all']>) => {
      state.rip_all = action.payload
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
      state.rip_all = [...state.sort_info.main_indexes, ...state.sort_info.extra_indexes].filter(uniqueFilter).length == state.toc_length
    },
    setExtraIndexes: (state, action: PayloadAction<number[]>) => {
      state.sort_info.extra_indexes = action.payload
      state.rip_all = [...state.sort_info.main_indexes, ...state.sort_info.extra_indexes].filter(uniqueFilter).length == state.toc_length
    },
    addMainIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.main_indexes.push(action.payload)
      state.sort_info.main_indexes.sort()
      state.sort_info.main_indexes = state.sort_info.main_indexes.filter(uniqueFilter)
      state.rip_all = [...state.sort_info.main_indexes, ...state.sort_info.extra_indexes].filter(uniqueFilter).length == state.toc_length
    },
    addExtraIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.extra_indexes.push(action.payload)
      state.sort_info.extra_indexes.sort()
      state.sort_info.extra_indexes = state.sort_info.extra_indexes.filter(uniqueFilter)
      state.rip_all = [...state.sort_info.main_indexes, ...state.sort_info.extra_indexes].filter(uniqueFilter).length == state.toc_length
    },
    removeMainIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.main_indexes = state.sort_info.main_indexes.filter((value) => value !== action.payload)
      state.rip_all = [...state.sort_info.main_indexes, ...state.sort_info.extra_indexes].filter(uniqueFilter).length == state.toc_length
    },
    removeExtraIndex: (state, action: PayloadAction<number>) => {
      state.sort_info.extra_indexes = state.sort_info.extra_indexes.filter((value) => value !== action.payload)
      state.rip_all = [...state.sort_info.main_indexes, ...state.sort_info.extra_indexes].filter(uniqueFilter).length == state.toc_length
    },
    setTocLength: (state, action: PayloadAction<number | undefined>) => {
      state.toc_length = action.payload
    },
    setName: (state, action: PayloadAction<string>) => {
      state.sort_info.name = action.payload
    },
    setId: (state, action: PayloadAction<string>) => {
      state.sort_info.id = action.payload
    },
    setFirstEpisode: (state, action: PayloadAction<number>) => {
      state.sort_info.first_episode = action.payload
    },
    setSeasonNumber: (state, action: PayloadAction<number>) => {
      state.sort_info.season_number = action.payload
    }
  }
})

export const ripActions = ripSlice.actions

export default ripSlice.reducer