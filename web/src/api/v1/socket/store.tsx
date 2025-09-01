import type { ProgressMessageEvent } from "@/components/socket/Context";
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { initialApiState } from "../state/types";

export type SocketProgress = {
  buffer?: number | null;
  progress?: number | null
}

export interface SocketState {
  ripState: {
    current_title?: number | null;

    current_progress?: SocketProgress[]
    total_progress?: SocketProgress

    current_status?: ProgressMessageEvent["name"];
    total_status?: string | null;

    rip_started?: boolean;

    connected?: boolean;
  }
  messages: string[]
}

const initialState: SocketState = {
  ...initialApiState.redux.socket
}

const socketSlice = createSlice({
  name: "socket",
  initialState,
  reducers: {
    updateSocketState: (state, action: PayloadAction<SocketState['ripState'] | undefined>) => {
      if (action.payload) {
        state.ripState = { ...state.ripState, ...action.payload }
      }
    },
    resetSocketState: (state, action: PayloadAction<SocketState['ripState']> ) => {
      state.ripState = { ...initialState.ripState, ...action.payload }
    },
    appendToMessages: (state, action: PayloadAction<string>) => {
      if (!state.messages) state.messages = []
      state.messages = state.messages.concat(action.payload).slice(-100)
    }
  }
})

export const socketActions = socketSlice.actions

export default socketSlice.reducer