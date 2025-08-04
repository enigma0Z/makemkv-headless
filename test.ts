export type BaseSocketMessage {
  type: string;
}

export type PingMessage = BaseSocketMessage & {
  type: "PingMessage" = "PingMessage";
  message: "ping" | "pong";
}

const v: PingMessage = {message: "ping"}

print(v)