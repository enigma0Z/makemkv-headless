import { BACKEND } from '@/api/endpoints';
import { io, Socket } from 'socket.io-client';
import type { ClientToServerEvents, ServerToClientEvents } from './Context';

export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io(BACKEND);