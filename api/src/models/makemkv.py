
from enum import Enum
from typing import Literal
from pydantic import BaseModel

def get_message_type(raw: str):
  return raw.split(':')[0]

type Progress = Literal['current', 'total']

class MakeMKVDataModel(BaseModel):
  raw: str
  mkv_type: str

  def __init__(self, **kwargs):
    assert 'raw' in kwargs, 'MakeMKVModels must include a raw field'
    kwargs['mkv_type'] = get_message_type(kwargs['raw'])
    errors = []
    for class_name in [cls.__name__ for cls in self.__class__.mro()]: 
      for message in MKVModels:
        if class_name == message.value.__name__:
          break
      else:
        errors.append(class_name)
        continue
      break
    else:
      raise ValueError(f'Could not find a valid MKVMessage for {self.__class__.__name__}, maybe it isnt in the inheritance tree? {errors}')
    super().__init__(**kwargs)

class ProgressModel(MakeMKVDataModel):
  code: int
  index: int
  name: str
  progress_type: Progress

  def __init__(self, raw: str, **kwargs):
    code = int(raw.split(':')[1].split(',')[0])
    index = int(raw.split(':')[1].split(',')[1])
    name = str(raw.split(':')[1].split(',')[2]).strip('"')
    super().__init__(raw=raw, code=code, index=index, name=name, **kwargs)

class CurrentProgressModel(ProgressModel):
  progress_type: Progress = 'current'

class TotalProgressModel(ProgressModel):
  progress_type: Progress = 'total'

class ProgressValueModel(MakeMKVDataModel):
  current: int
  total: int
  max: int
  
  def __init__(self, raw: str):
    current, total, max = [ 
      int(value) 
      for value 
      in raw.split(':')[1].split(',') 
    ]
    super().__init__(raw=raw, current=current, total=total, max=max)

class DriveInfoModel(MakeMKVDataModel):
  '''DRV'''
  index: int
  status: int
  name: str

  def __init__(self, raw: str):
    fields = raw.split(':')[0].split(',')
    index = int(fields[0])
    status = int(fields[1])
    name = fields[4].strip('"')
    super().__init__(raw=raw, index=index, status=status, name=name)

class TitleCountModel(MakeMKVDataModel):
  '''TCOUNT'''
  count: int

  def __init__(self, raw: str):
    count = raw.split(':')[1]
    super().__init__(raw=raw, count=count)

class BaseInfoModel(MakeMKVDataModel):
  id: tuple[int, int]
  value: str | int

  def __init__(self, raw: str, id_index=0, **kwargs):
    id = tuple([int(v) for v in raw.split(':')[1].split(',')[id_index:id_index+2]])
    value = [value.strip('"') for value in raw.split(':')[1].split(',')[id_index+2:]]
    if len(value) == 1:
      value = value[0]
      try:
        value = int(value)
      except ValueError:
        pass
    else: # Value is a list of something
      value = ' '.join([f'{v}' for v in value])

    super().__init__(raw=raw, id=id, value=value, **kwargs)

class SourceInfoModel(BaseInfoModel):
  '''CINFO'''

  def __init__(self, raw: str):
    super().__init__(raw=raw)

class TitleInfoModel(BaseInfoModel):
  '''
  TINFO:6,49,0,"B7"
  '''
  title_index: int

  def __init__(self, raw: str):
    title_index = int(raw.split(':')[1].split(',')[0])
    super().__init__(raw=raw, title_index=title_index, id_index=1)

class TrackInfoModel(BaseInfoModel):
  '''
  SINFO
  2025-08-06 09:19:28,847 [DEBUG] async_queue_interface.py:106 MainThread - Received BaseMessageEvent {'raw': 'SINFO:6,0,1,6201,"Video"', 'type': 'BaseMessageEvent'}
  '''
  source_index: int
  title_index: int

  def __init__(self, raw: str):
    title_index = int(raw.split(':')[1].split(',')[0])
    source_index = int(raw.split(':')[1].split(',')[1])
    super().__init__(raw=raw, title_index=title_index, source_index=source_index, id_index=2)

class MKVModels(Enum):
  PRGC = CurrentProgressModel
  PRGT = TotalProgressModel
  PRGV = ProgressValueModel
  CINFO = SourceInfoModel
  TINFO = TitleInfoModel
  SINFO = TrackInfoModel

def mkv_model_from_raw(raw: str):
  raw = raw.strip()
  id = raw.split(':')[0]
  return MKVModels[id].value

def from_raw(raw: str):
  model_cls = mkv_model_from_raw(raw)
  return model_cls(raw)