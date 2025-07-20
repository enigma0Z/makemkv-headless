import type { RipState } from "@/api/store/rip";
import type { TocState } from "@/api/store/toc";
import type { SocketProgress, SocketState } from "@/api/store/socket";

import type { ProgressMessageEvent } from "@/components/socket/Context";

export type ApiState = {
  redux: {
    rip?: RipState;
    toc?: TocState;
    socket: SocketState;
  }
  socket: {
    current_title?: number | null;

    current_progress?: SocketProgress[];
    total_progress?: SocketProgress;

    current_status?: ProgressMessageEvent["name"];
    total_status?: string;

    rip_started?: boolean;
  }
}

export const initialApiState: ApiState = {
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
      rip_all: false,
      toc_length: 0
    },
    toc: {
      lines: [],
      source: undefined
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
      }
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