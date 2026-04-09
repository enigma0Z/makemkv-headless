from types import NoneType
from typing import Literal, TypedDict, Union

from src.message.base_message_event import BaseMessageEvent


class RipStartStopMessageData(TypedDict):
  index: Union[int, NoneType]
  state: Literal["stop", "start"]

class RipStartStopMessageEvent(BaseMessageEvent):
  def __init__(self, **data):
    self.data: RipStartStopMessageData = {}
    assert 'index' in data
    try: 
      assert isinstance(data['index'], int)
    except:
      try: 
        data['index'] = int(data['index'])
      except ValueError:
        data['index'] = None

    assert 'state' in data
    assert data['state'] in ['start', 'stop']

    super().__init__(**data)
