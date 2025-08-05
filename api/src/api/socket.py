from fastapi import WebSocket

from src.models import socket as model

class SocketConnectionManager:
  def __init__(self):
    self.active_connections: list[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)

  def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)

  async def send(self, data: model.SocketMessage, websocket: WebSocket):
    await websocket.send_json(data.model_dump())

  async def broadcast(self, data: model.SocketMessage):
    for connection in self.active_connections:
      await self.send(data, connection)

socket = SocketConnectionManager()
