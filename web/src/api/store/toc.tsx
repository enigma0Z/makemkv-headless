import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type Toc = {

}

export type BaseInfo = {
  fields: string[];
}

export type SourceInfo = {
  titles: BaseInfo & TitleInfo[];
  name: string;
  name1: string;
  name2: string;
  name3: string;
  media: string;
}

export type TitleInfo = {
  tracks: BaseInfo & (
    BaseTrackInfo 
    | BaseTrackInfo & VideoTrackInfo 
    | BaseTrackInfo & AudioTrackInfo
  )[];
  chapters: string;
  runtime: string;
  size: string;
  segments: string;
  segments_map: string;
  filename: string;
  summary: string;
}

export type BaseTrackInfo = {
  stream_type?: string;
  stream_format?: string;
  stream_conversion_type?: string;
  stream_bitrate?: string;
  stream_detail?: string;
  stream_language_code?: string;
  stream_language?: string;
}

export type VideoTrackInfo = {
  video_resolution?: string;
  video_aspect_ratio?: string;
  video_framerate?: string;
}

export type AudioTrackInfo = {
  audio_format?: string
}

export interface TocState {
  lines?: string[];
  source?: BaseInfo & SourceInfo;
}

const initialState: TocState = {
  lines: [],
  source: undefined
}

const tocSlice = createSlice({
  name: "toc",
  initialState,
  reducers: {
    setTocData: (state, action: PayloadAction<TocState | undefined>) => {
      console.log('setTocData', action)
      if (action.payload) {
        state.lines = action.payload.lines
        state.source = action.payload.source
      } else {
        state.lines = []
        state.source = undefined
      }
    }
  }
})

export const tocActions = tocSlice.actions

export default tocSlice.reducer