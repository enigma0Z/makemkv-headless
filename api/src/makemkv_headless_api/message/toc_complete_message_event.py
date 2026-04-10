from typing import Literal, TypedDict

from makemkv_headless_api.message.base_message_event import BaseMessageEvent
from makemkv_headless_api.toc import Toc


class TocCompleteMessageData(TypedDict):
  status: Literal["started", "complete"]

class TocStatusMessageEvent(BaseMessageEvent):
  def __init__(self, status, **kwargs):
    self.data: TocCompleteMessageData = {}
    super().__init__(**kwargs)
