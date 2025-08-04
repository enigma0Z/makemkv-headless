export type BaseSocketMessage {
  type: string;
}

export type PingMessage = BaseSocketMessage & {
  type: "PingMessage";
  message: "ping" | "pong";
}