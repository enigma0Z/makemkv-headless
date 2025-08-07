import logging

from src.api.socket import socket
from src.models import socket as model

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/socket")

@router.websocket('')
@router.websocket('/')
async def websocket_root(websocket: WebSocket):
  await socket.connect(websocket)
  try:
    while True:
      data = await websocket.receive_json()
      try:
        message = getattr(model, data['type'])(**data)
        # logger.debug(f'{websocket} received {message}')

        if isinstance(message, model.ClientPingMessage):
          await socket.send(model.ServerPongMessage(), websocket)
      except AttributeError as ex:
        logger.error(f'Received unknown socket message {data}, Exception was {ex}')
  except WebSocketDisconnect:
    logger.debug('Socket disconnect')
    socket.disconnect(websocket)
