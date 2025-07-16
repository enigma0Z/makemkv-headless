from json import loads
import logging
from re import match
from types import NoneType
from typing import Literal, TypedDict, Union

from src.json_serializable import JSONSerializable

logger = logging.getLogger(__name__)

class BaseMessageEvent(JSONSerializable):
  def __init__(self, **data):
    self.data = data
    self.data['type'] = type(self).__name__

  def __setattr__(self, name, value):
    if (name == 'data'):
      self.__dict__['data'] = value
    else:
      self.data[name] = value

  def __getattr__(self, name):
    if (name == 'data'):
      return self.data
    else:
      return self.data.get(name)

class MessageEvent(BaseMessageEvent):
  def __init__(self, *text, sep=' ', end="\n", **data):
    super().__init__(**data)
    try:
      if len(text) > 0:
        assert "text" not in data
        self.data['text'] = sep.join([ str(item) for item in text ]) + end
      else:
        self.data['text'] = match(r'.+?,"(.+?)".*', data['raw']).groups()[0]
    except Exception as ex:
      self.data['text'] = str(ex)
    
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