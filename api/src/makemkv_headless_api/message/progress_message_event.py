from typing import Literal, TypedDict

from src.message.base_message_event import BaseMessageEvent


type StatusMessage = Literal[
  "Scanning CD-ROM devices",
  "Opening DVD disc",
  "Processing title sets",
  "Scanning contents",
  "Processing titles",
  "Decrypting data",
  "Saving all titles to MKV files",
  "Analyzing seamless segments",
  "Saving to MKV file"
]

class ProgressMessageData(TypedDict):
  code: int
  index: int
  name: StatusMessage
  progress_type: Literal['current', 'total']

class ProgressMessageEvent(BaseMessageEvent):
  '''PRGC:5057,0,"Analyzing seamless segments"'''
  def __init__(self, **data):
    self.data:ProgressMessageData = {}
    super().__init__(**data)
    assert "raw" in data
    messageType = self.data['raw'].split(':')[0]
    if (messageType == 'PRGC'):
      self.data['progress_type'] = 'current'
    elif (messageType == 'PRGT'):
      self.data['progress_type'] = 'total'
    self.data['code'] = int(self.data['raw'].split(':')[1].split(',')[0])
    self.data['index'] = int(self.data['raw'].split(':')[1].split(',')[1])
    self.data['name'] = str(self.data['raw'].split(':')[1].split(',')[2]).strip('"')
