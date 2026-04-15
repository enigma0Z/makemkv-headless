import type { ApiError } from "../error/types";

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

export type MkvLogMessage = BaseMessageType & {
  code: number[];
  text: string;
}

export type TocStatusMessage = BaseMessageType & {
  state: "running" | "complete";
}

export type RipStartStopMessage = BaseMessageType & {
  index: number | null;
  state: "start" | "stop";
}

export type ErrorMessage = BaseMessageType & {
  error: ApiError
}

export type ServerToClientMessages = 
  "LogMessage" | 
  "MkvLogMessage" |
  "TocStatusMessage" |
  "CurrentProgressMessage" |
  "TotalProgressMessage" |
  "ProgressValueMessage" |
  "RipStartStopMessage" |
  "ErrorMessage"

export function isRippingStatus(status: string | undefined) {
  return (
    status === "Analyzing seamless segments"
    || status === "Saving to MKV file"
  )
}

export interface ClientMessage {
  type: string
}

export class ClientPingMessage implements ClientMessage {
  type: string
  message: PingPongMessage

  constructor(message: PingPongMessage) {
    this.type = 'ClientPingMessage'
    this.message = message
  }
}
