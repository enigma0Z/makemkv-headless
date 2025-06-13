import type { RipState } from "@/api/store/rip";
import type { TocState } from "@/api/store/toc";
import type { ProgressMessageEvent } from "@/components/socket/Context";

export type ApiState = {
  redux: {
    rip?: RipState;
    toc?: TocState;
  }
  socket: {
    current_title?: number;

    current_progress?: {buffer?: number, progress: number}[];
    total_progress?: {buffer: number, progress: number};

    current_status?: ProgressMessageEvent["name"];
    total_status?: string;

    rip_started?: boolean;
  }
}

export const initialApiState: ApiState = {
  redux: {
    rip: undefined,
    toc: undefined
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