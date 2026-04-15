import type { RipState } from "@/api/v1/rip/store";
import type { TocState } from "@/api/v1/toc/store";
import type { SocketProgress, SocketState } from "@/api/v1/socket/store";

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
  redux: {
    rip?: RipState;
    toc?: TocState;
    socket: SocketState;
  }
  socket: {
    current_title?: number | null;

    current_progress?: SocketProgress[];
    total_progress?: SocketProgress;

    current_status?: CurrentStatus;
    total_status?: string;

    rip_started?: boolean;
    
  }
}

export const initialApiState: State = {
  redux: {
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
      ripState: {
        current_title: undefined,
        current_progress: [],
        total_progress: {
          buffer: null,
          progress: null
        },
        current_status: undefined,
        total_status: undefined,
        rip_started: false
      },
      messages: []
    }
  },
  socket: {
    current_title: undefined,
    current_progress: undefined,
    total_progress: undefined,
    current_status: undefined,
    total_status: undefined,
    rip_started: false
  }
}