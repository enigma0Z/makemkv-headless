import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { initialApiState, type CurrentStatus } from "../state/types";

export type SocketProgress = {
  buffer?: number | null;
  progress?: number | null
}

export interface SocketState {
  rip: {
    current_title?: number | null;

    current_progress?: SocketProgress[]
    total_progress?: SocketProgress

    current_status?: CurrentStatus;
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
    updateSocketState: (state, action: PayloadAction<SocketState['rip'] | undefined>) => {
      if (action.payload) {
        state.rip = { ...state.rip, ...action.payload }
      }
    },
    setSocketState: (state, action: PayloadAction<SocketState['rip'] | undefined>) => {
      state.rip = { ...initialState.rip, ...(action?.payload ?? {}) }
    },
    appendToMessages: (state, action: PayloadAction<string>) => {
      if (!state.messages) state.messages = []
      state.messages = state.messages.concat(action.payload).slice(-100)
    }
  }
})

export const socketActions = socketSlice.actions

export default socketSlice.reducer