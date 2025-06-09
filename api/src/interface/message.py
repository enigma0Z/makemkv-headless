from json import loads
import logging
from re import match

from json_serializable import JSONSerializable

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
    if len(text) > 0:
      assert "text" not in data
      self.data['text'] = sep.join(text) + end
    else:
      self.data['text'] = match(r'.+?,"(.+?)".*', data['raw']).groups()[0]
    
class ProgressMessageEvent(BaseMessageEvent):
  '''PRGC:5057,0,"Analyzing seamless segments"'''
  def __init__(self, **data):
    super().__init__(**data)
    logger.debug(f'ProgressMessageEvent.__init__(), data: {data}, self.data: {self.data}')
    # PRGC:code,id,name (Current)
    # PRGT:code,id,name (Current)
    assert "raw" in data
    messageType = self.data['raw'].split(':')[0]
    if (messageType == 'PRGC'):
      self.data['progressType'] = 'Current'
    elif (messageType == 'PRGT'):
      self.data['progressType'] = 'Total'
    self.data['code'] = int(self.data['raw'].split(':')[1].split(',')[0])
    self.data['index'] = int(self.data['raw'].split(':')[1].split(',')[1])
    self.data['name'] = str(self.data['raw'].split(':')[1].split(',')[2]).strip('"')

class ProgressValueMessageEvent(BaseMessageEvent):
  def __init__(self, **data):
    super().__init__(**data)
    self.data['current'], self.data['total'], self.data['max'] = [ 
      int(value) 
      for value 
      in data['raw'].split(':')[1].split(',') 
    ]

class RipStartMessageEvent(BaseMessageEvent):
  def __init__(self, **data):
    assert 'index' in data
    try: 
      assert isinstance(data['index'], int)
    except:
      try: 
        data['index'] = int(data['index'])
      except ValueError:
        data['index'] = None

    super().__init__(**data)

class ProcessStartStopEvent(BaseMessageEvent):
  '''
  * `state`: Whether the process is starting or stopping,  `start` or `stop`
  * `name`: The name of the process
  '''
  def __init__(self, **data):
    assert 'state' in data
    assert data['state'] in ['start', 'stop']
    assert 'name' in data
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