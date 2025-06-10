import { createContext, useState } from "react";

export type BaseMessageEventData = { // message.py BaseMessage
  type: string;
}

export type ProgressMessageEvent = BaseMessageEventData & {
    code: number;
    index: number;
    name: "Scanning CD-ROM devices"
      | "Opening DVD disc"
      | "Processing title sets"
      | "Scanning contents"
      | "Processing titles"
      | "Decrypting data"
      | "Saving all titles to MKV files"
      | "Analyzing seamless segments"
      | "Saving to MKV file";
    progressType: "Current" | "Total";
}

export type ProgressValueMessageEvent = BaseMessageEventData & {
  current: number;
  total: number;
  max: number;
}

export type MessageEvent = BaseMessageEventData & {
  text: string
}

export type RipStartStopMessageEvent = BaseMessageEventData & {
  index: number | null;
  state: "start" | "stop";
}

export interface ServerToClientEvents {
  ProgressMessageEvent: (value: ProgressMessageEvent) => void;
  ProgressValueMessageEvent: (value: ProgressValueMessageEvent) => void;
  MessageEvent: (value: MessageEvent) => void;
  RipStartStopMessageEvent: (value: RipStartStopMessageEvent) => void;
}

export interface ClientToServerEvents { }

export type SetStateCallback<T> = React.Dispatch<React.SetStateAction<T>>

type RipState = {
  currentTitle?: number;
  currentProgress?: {buffer?: number, progress: number}[];
  totalProgress?: {buffer: number, progress: number};
  currentStatus?: ProgressMessageEvent["name"];
  totalStatus?: string;
  ripStarted?: boolean;
}

type ContextProps = {
  connected: boolean
  setConnected: React.Dispatch<React.SetStateAction<boolean>>

  progressMessageEvents?: (ProgressMessageEvent)[];
  setProgressMessageEvents?: SetStateCallback<ProgressMessageEvent[] | undefined>;

  progressValueMessageEvents?: (ProgressValueMessageEvent)[];
  setProgressValueMessageEvents?: SetStateCallback<ProgressValueMessageEvent[] | undefined>;

  messageEvents?: (MessageEvent)[];
  setMessageEvents?: SetStateCallback<MessageEvent[] | undefined>;

  ripStartStopMessageEvents?: (RipStartStopMessageEvent)[];
  setRipStartStopMessageEvents?: SetStateCallback<RipStartStopMessageEvent[] | undefined>;

  ripState?: RipState;
  setRipState?: SetStateCallback<RipState | undefined>;
}

export const Context = createContext<ContextProps>({
  connected: false,
  setConnected: () => {},
})

type SocketContextProps = {
  children: React.ReactNode
}

const SocketContext = ({ children }: SocketContextProps) => {
  const [connected, setConnected] = useState<boolean>(false)
  const [progressMessageEvents, setProgressMessageEvents] = useState<(ProgressMessageEvent)[]>()
  const [progressValueMessageEvents, setProgressValueMessageEvents] = useState<(ProgressValueMessageEvent)[]>()
  const [messageEvents, setMessageEvents] = useState<(MessageEvent)[]>()
  const [ripStartStopMessageEvents, setRipStartStopMessageEvents] = useState<(RipStartStopMessageEvent)[]>()
  const [ripState, setRipState] = useState<RipState>()

  return <Context value={{
    connected, setConnected,
    progressMessageEvents, setProgressMessageEvents,
    progressValueMessageEvents, setProgressValueMessageEvents,
    messageEvents, setMessageEvents,
    ripStartStopMessageEvents, setRipStartStopMessageEvents,
    ripState, setRipState
  }}>
    {children}
  </Context>
};

export default SocketContext