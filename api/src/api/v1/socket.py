import logging
import json

import models.socket as socket_models

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
logger = logging.getLogger(__name__)

class SocketConnectionManager:
  def __init__(self):
    self.active_connections: list[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)

  def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)

  async def send(self, data: socket_models.BaseSocketMessageModel, websocket: WebSocket):
    await websocket.send_json(data.model_dump())

  async def broadcast(self, data: socket_models.BaseSocketMessageModel):
    for connection in self.active_connections:
      await self.send(data, connection)

socket = SocketConnectionManager()

router = APIRouter(prefix="/socket")

@router.websocket('')
@router.websocket('/')
async def websocket_root(websocket: WebSocket):
  await socket.connect(websocket)
  try:
    while True:
      data = await websocket.receive_json()
      message = getattr(socket_models, data['type'])(**data)
      logger.debug(f'Websocket message received: {message}')

      if isinstance(message, socket_models.PingMessage):
        await socket.send(socket_models.PingMessage(message="pong"), websocket)
  except WebSocketDisconnect:
    socket.disconnect(websocket)


# @SOCKET.on('connect')
# def socket_on_connect(*args, **kwargs):
#   logger.debug(f'{args}, {kwargs}')

# @SOCKET.on('disconnect')
# def socket_on_disconnect(*args, **kwargs):
#   logger.debug(f'{args}, {kwargs}')