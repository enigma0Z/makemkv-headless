from typing import Generic, Literal, TypeVar
from pydantic import BaseModel

from src.models.makemkv import CurrentProgressModel, MkvLogModel, ProgressModel, ProgressValueModel, SourceInfoModel, TitleInfoModel, TotalProgressModel, TrackInfoModel, mkv_model_from_raw

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
  index: int = None
  state: Literal['stop', 'start']

# MKV Messages
class ProgressMessage(SocketMessage): ...
class CurrentProgressMessage(CurrentProgressModel, ProgressMessage): ...
class TotalProgressMessage(TotalProgressModel, ProgressMessage): ...
class ProgressValueMessage(ProgressValueModel, SocketMessage): ...
class SourceInfoMessage(SourceInfoModel, SocketMessage): ...
class TitleInfoMessage(TitleInfoModel, SocketMessage): ...
class TrackInfoMessage(TrackInfoModel, SocketMessage): ...
class MkvLogMessage(MkvLogModel, SocketMessage): ...

def mkv_message_class_from_raw(raw: str):
  model_cls = mkv_model_from_raw(raw)
  message_cls = globals()[model_cls.__name__.replace('Model', 'Message')]
  return message_cls

def mkv_message_from_raw(raw: str):
  try: 
    message_cls = mkv_message_class_from_raw(raw)
    return message_cls(raw)
  except KeyError:
    return LogMessage(message=raw)