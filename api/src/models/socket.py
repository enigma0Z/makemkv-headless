from typing import Generic, Literal, TypeVar, TypedDict
from pydantic import BaseModel

from time import time

T = TypeVar('T')

class SocketMessage(BaseModel, Generic[T]):
  type: str

  def __init__(self, **kwargs):
    kwargs['type'] = self.__class__.__name__
    super().__init__(**kwargs)

  def __getitem__(self, key):
    return self.__dict__[key]

class PingMessage(SocketMessage):
  type Message = Literal['ping', 'pong']

  message: Message
  time: int


class LogDataModel(SocketMessage):
  text: str
