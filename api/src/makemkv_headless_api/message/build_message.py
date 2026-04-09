from src.message.base_message_event import BaseMessageEvent
from src.message.message_event import MessageEvent
from src.message.progress_message_event import ProgressMessageEvent
from src.message.progress_value_message_event import ProgressValueMessageEvent

import logging
logger = logging.getLogger(__name__)

def build_message(**data):
  assert "raw" in data
  if data['raw'].startswith("MSG"): 
    return MessageEvent(**data)
  elif data['raw'].startswith("PRGC") or data['raw'].startswith("PRGT"):
    return ProgressMessageEvent(**data)
  elif data['raw'].startswith("PRGV"):
    return ProgressValueMessageEvent(**data)
  else:
    return BaseMessageEvent(**data)