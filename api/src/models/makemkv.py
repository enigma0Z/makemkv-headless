
from enum import Enum
from typing import Literal
from pydantic import BaseModel

class MKVMessages(Enum):
  CurrentProgressModel = "PRGC"
  TotalProgressModel = "PRGT"
  ProgressValueModel = "PRGV"

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
    for name in [cls.__name__ for cls in self.__class__.mro()]: 
      try:
        assert kwargs['mkv_type'] == MKVMessages[name].value, f'{name}; {kwargs['mkv_type']} != {MKVMessages[name].value}'
        break
      except (KeyError, AssertionError) as ex:
        errors.append(ex)
        pass
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
