import type { RipState } from "@/api/v1/rip/store";
import type { TocState } from "@/api/v1/toc/store";
import type { SocketState } from "@/api/v1/socket/store";

export type CurrentStatus = "Scanning CD-ROM devices"
  | "Opening DVD disc"
  | "Processing title sets"
  | "Scanning contents"
  | "Processing titles"
  | "Decrypting data"
  | "Saving all titles to MKV files"
  | "Analyzing seamless segments"
  | "Saving to MKV file";

export type State = {
  rip?: RipState;
  toc?: TocState;
  socket: SocketState;
}

export const initialApiState: State = {
  rip: {
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
  },
  toc: {
    lines: [],
  },
  socket: {
    rip: {
      current_title: undefined,
      current_progress: [],
      total_progress: {
        buffer: null,
        progress: null
      },
      current_status: undefined,
      total_status: undefined,
      started: false
    },
    connected: false,
    messages: []
  }
}