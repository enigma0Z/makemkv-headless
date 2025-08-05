from typing import Generic, Literal, TypeVar
from pydantic import BaseModel

from src.models.makemkv import CurrentProgressModel, ProgressModel, ProgressValueModel, TotalProgressModel

T = TypeVar('T')

class SocketMessage(BaseModel):
  type: str

  def __init__(self, **kwargs):
    kwargs['type'] = self.__class__.__name__
    super().__init__(**kwargs)

  def __getitem__(self, key):
    return self.__dict__[key]

class ClientPingMessage(SocketMessage):
  message: str = "ping"

class ServerPongMessage(SocketMessage):
  message: str = "pong"

class LogMessage(SocketMessage):
  message: str

class RipStartStopMessage(SocketMessage):
  index: int
  state: Literal['stop', 'start']

class ProgressMessage(SocketMessage): ...

class CurrentProgressMessage(ProgressMessage, CurrentProgressModel): ...

class TotalProgressMessage(ProgressMessage, TotalProgressModel): ...

class ProgressValueMessage(SocketMessage, ProgressValueModel): ...

