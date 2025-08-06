import logging
from fastapi import WebSocket

from src.models import socket as model

logger = logging.getLogger(__name__)

class SocketConnectionManager:
  def __init__(self):
    self.active_connections: list[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)
    logger.debug(f'{self} Connection established with {websocket}, active connections: {self.active_connections}')

  def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)
    logger.debug(f'Connection closed with {websocket}, active connections: {self.active_connections}')

  async def send(self, data: model.SocketMessage, websocket: WebSocket):
    await websocket.send_json(data.model_dump())

  async def broadcast(self, data: model.SocketMessage):
    logger.debug(f'{self} Broadcasting message {data.type} to {self.active_connections}')
    for connection in self.active_connections:
      logger.debug(f'Sending broadcast to {connection}')
      await self.send(data, connection)

socket = SocketConnectionManager()

# 0x104e69fd0
# 0x104e69fd0
# 0x107369fd0