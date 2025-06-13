from typing import TypedDict, Union
from deepmerge import Merger

from src.json_serializable import JSONSerializable

class RipDestination(TypedDict, total=False):
  library: str
  media: str
  content: str

class RipSortInfo(TypedDict, total=False):
  name: str
  id: str
  first_episode: int
  season_number: int
  main_indexes: list[int]
  extra_indexes: list[int]
  split_segments: list[int]
  id_db: str

class ReduxRipState(TypedDict, total=False):
  destination: RipDestination
  sort_info: RipSortInfo
  rip_all: bool
  toc_length: int

class ProgressState(TypedDict, total=False):
  buffer: float
  progress: float

class RipState(TypedDict, total=False):
  redux: ReduxRipState
  currentTitle: int
  currentProgress: list[ProgressState]
  totalProgress: ProgressState
  currentStatus: str
  totalStatus: str
  ripStarted: bool

class State(JSONSerializable):
  def __init__(self):
    self.data: RipState = {
      'redux': {},
      'currentTitle': None,
      'currentProgress': [],
      'totalProgress': {
        'buffer': None,
        'progress': None
      },
      'currentStatus': None,
      'totalStatus': None,
      'ripStarted': False
    }
    self.merger = Merger( [(dict, "merge")], ["override"], ["override"])

  def json_encoder(self):
    return self.data

  def update_from_partial(self, data):
    self.data = self.merger(self.data, data)

  def update_current_progress(self, index: int, progress: int, buffer: Union[int, None] = None):
    if len(self.data['currentProgress']) <= index:
      self.data['currentProgress'] = [ 
        self.data['currentProgress'][index] 
        if len(self.data['currentProgress']) < index
        else {"buffer": None, "progress": None}
        for index in range(0, self.data['currentTitle']+1)
      ]
    
    self.data['currentProgress'][index]['progress'] = progress
    if buffer != None:
      self.data['currentProgress'][index]['buffer'] = buffer
  
STATE = State()