import { store } from "@/api/store";
import { socketActions } from "@/api/store/socket";
import type { BaseSocketMessage, PingMessage } from "@/models/socket";

// export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io(BACKEND);

class SocketConnection {
  url: string;
  socket: WebSocket | null = null;
  connected: boolean = false;

  pingInterval: number;
  pingFailures: number = 3
  // connectInterval: number = 1000

  pingTimestamp: number;
  pongTimestamp: number;

  pingTimeout: number | null = null;
  connectTimeout: number | null = null;

  messageHandlers: {[index: string]: <T>(data: T) => void} = {}

  constructor(url: string, interval: number = 5000) {
    this.url = url;
    this.pingInterval = interval
    this.pingTimestamp = Date.now()
    this.pongTimestamp = Date.now()
  }

  connect() {
    console.debug('connecting...')
    this.socket = new WebSocket(this.url);

    this.socket.onopen = (event) => {
      console.debug('Socket open', event)
      if (this.connectTimeout !== null) {
        clearTimeout(this.connectTimeout)
        this.connectTimeout = null
      }
      store.dispatch(socketActions.updateSocketState({ connected: true }))
      this.connected = true
      this.ping()
    }

    this.socket.onmessage = (event) => {
      this.handleMessage(JSON.parse(event.data))
    }
    
    this.socket.onclose = (event) => {
      console.debug('Socket close', event)
      this.connected = false

      if (this.pingTimeout !== null) {
        clearTimeout(this.pingTimeout)
        this.pingTimeout = null
      }

      if (this.connectTimeout === null) {
        this.reconnect()
      }
    }

    this.socket.onerror = (event) => {
      console.debug('Socket error', event)
    }
  }

  handleMessage(data: BaseSocketMessage) {
    console.debug('Socket message', data)
    if (data.type === 'PingMessage') {
      if ((data as PingMessage).message == "pong") {
        this.pongTimestamp = Date.now()
      }
    } else if (data.type in this.messageHandlers) {
      this.messageHandlers[data.type](data)
    }
  }

  ping() {
    this.pingTimestamp = Date.now()

    if (this.socket && this.pingTimestamp - this.pongTimestamp > this.pingInterval * this.pingFailures) {
      this.socket.close()
    } else {
      this.send<PingMessage>({type: "PingMessage", message: "ping" })
      this.pingTimeout = setTimeout(
        () => { this.ping() },
        this.pingInterval
      )
    }
  }

  reconnect() {
    if (!this.connected) {
      console.debug('Attempting to (re)connect')
      this.connect()
      this.connectTimeout = setTimeout(
        () => this.reconnect(),
        this.pingInterval
      )
    }
  }

  send<T>(data: T) {
    this.socket && this.socket.send(JSON.stringify(data))
  }

  on(message: string, handler: <T>(data: T) => void) {
    this.messageHandlers[message] = handler
  }
}

export const socket = new SocketConnection(`ws://${window.location.hostname}:4000/api/v1/socket`)

socket.connect()