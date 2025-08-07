import { store } from "@/api/store";
import { socketActions } from "@/api/store/socket";
import { ClientPingMessage, type BaseMessageType } from "@/models/socket";

export class SocketConnection { 
  url: string;
  socket: WebSocket | null = null;
  connected: boolean = false;

  pingInterval: number;
  pingFailures: number = 3;

  pingTimestamp: number = Date.now();
  pongTimestamp: number = Date.now();

  pingTimeout: number | null = null;
  connectTimeout: number | null = null;

  messageHandlers: {[index: string]: (event: any) => void} = {}

  constructor(url: string, interval: number = 5000) {
    this.url = url;
    this.pingInterval = interval
  }

  connect() {
    console.debug('connecting...')
    this.socket = new WebSocket(this.url);

    this.socket.onopen = (event) => {
      console.debug('Socket open', event)
      this.pingTimestamp = Date.now()
      this.pongTimestamp = Date.now()

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

  handleMessage(data: BaseMessageType) {
    if (data.type === 'ServerPongMessage') {
      this.pongTimestamp = Date.now()
    } else if (data.type in this.messageHandlers) {
      if (data.type !== 'ProgressValueMessage')
        console.debug(data.type, data)
      this.messageHandlers[data.type](data)
    } else {
      console.info('Received unhandled message', data.type, data)
    }
  }

  ping() {
    this.pingTimestamp = Date.now()

    if (this.socket && this.pingTimestamp - this.pongTimestamp > this.pingInterval * this.pingFailures) {
      console.log('Closing socket', this.pingTimestamp, this.pongTimestamp, this.pingTimestamp - this.pongTimestamp)
      this.socket.close()
    } else {
      this.send(new ClientPingMessage("ping"))
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

  on(event: string, callback: (event: any) => void) {
    this.messageHandlers[event] = callback
  }
}