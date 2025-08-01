from typing import TypedDict

from src.message.base_message_event import BaseMessageEvent


class ProgressValueMessageData(TypedDict):
  current: int
  total: int
  max: int

class ProgressValueMessageEvent(BaseMessageEvent):
  def __init__(self, **data):
    self.data: ProgressValueMessageData = {}
    super().__init__(**data)
    self.data['current'], self.data['total'], self.data['max'] = [ 
      int(value) 
      for value 
      in data['raw'].split(':')[1].split(',') 
    ]
