export interface EventsMap {
    [index: string]: any;
}

export interface DefaultEventsMap {
    [event: string]: (...args: any[]) => void;
}

type PingPongMessage = "ping" | "pong"

export type BaseMessageType = { // message.py BaseMessage
  type: string;
}

export type ServerPongMessage = BaseMessageType & {
  message: "pong"
}

export type ProgressMessage = BaseMessageType & {
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
    progress_type: "current" | "total";
}

export type ProgressValueMessage = BaseMessageType & {
  current: number;
  total: number;
  max: number;
}

export type LogMessage = BaseMessageType & {
  message: string
}

export type RipStartStopMessage = BaseMessageType & {
  index: number | null;
  state: "start" | "stop";
}

export interface ServerToClientEvents {
  ProgressMessage: (value: ProgressMessage) => void;
  ProgressValueMessage: (value: ProgressValueMessage) => void;
  LogMessage: (value: LogMessage) => void;
  RipStartStopMessage: (value: RipStartStopMessage) => void;
}

export function isRippingStatus(status: string | undefined) {
  return (
    status === "Analyzing seamless segments"
    || status === "Saving to MKV file"
  )
}

export class ClientMessage {
  type: string

  constructor() {
    this.type = this.constructor.name
  }
}

export class ClientPingMessage extends ClientMessage {
  message: PingPongMessage

  constructor(message: PingPongMessage) {
    super()
    this.message = message
  }
}
