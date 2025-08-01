from typing import TypedDict

from src.message.base_message_event import BaseMessageEvent
from src.toc import TOC


class TOCCompleteMessageData(TypedDict):
  toc: TOC

class TOCCompleteMessageEvent(BaseMessageEvent):
  def __init__(self, **data):
    self.data: TOCCompleteMessageData = {}
    assert 'toc' in data
    self.data = data
    super().__init__(**data)
