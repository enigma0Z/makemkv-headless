import logging
from typing import TypedDict
from deepmerge import Merger

from src.json_serializable import JSONSerializable
from src.message.progress_message_event import ProgressMessageData, StatusMessage
from src.message.progress_value_message_event import ProgressValueMessageData
from src.toc import TOC

logger = logging.getLogger(__name__)

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

class ReduxState(TypedDict, total=False):
  rip: ReduxRipState
  toc: TOC

class ProgressState(TypedDict, total=False):
  buffer: float
  progress: float

class SocketStatus(TypedDict, total=False):
  current_title: int
  current_progress: list[ProgressState]
  total_progress: ProgressState
  current_status: StatusMessage
  total_status: StatusMessage
  rip_started: bool

SOCKET_STATUS_DEFAULT_VALUE: SocketStatus = {
  'current_title': None,
  'current_progress': [],
  'total_progress': {
    'buffer': None,
    'progress': None
  },
  'current_status': None,
  'total_status': None,
  'rip_started': False
}

class StateData(TypedDict, total=False):
  redux: ReduxState
  socket: SocketStatus

class State(JSONSerializable):
  def __init__(self):
    self.reset_all()
    self.merger = Merger( [(dict, "merge")], ["override"], ["override"])

  def json_encoder(self):
    return self.data

  def reset_all(self): 
    self.data: StateData = {
      'redux': {},
      'socket': { **SOCKET_STATUS_DEFAULT_VALUE }
    }

  def reset_socket(self):
    self.data['socket'] = { **SOCKET_STATUS_DEFAULT_VALUE }

  def update_from_partial(self, data):
    self.data = self.merger(self.data, data)

  def fill_progress_indexes(self, index):
    if len(self.data['socket']['current_progress']) <= index:
      # Create empty current_progress entries as needed
      self.data['socket']['current_progress'] = [ 
        self.data['socket']['current_progress'][index] 
        if len(self.data['socket']['current_progress']) > index
        else {"buffer": None, "progress": None}
        for index in range(0, index+1)
      ]
    pass

  def update_progress(self, data: ProgressValueMessageData):
    self.data['socket']['total_progress']['progress'] = data['total'] / data['max']
    if (self.data['socket']['current_title'] != None):
      self.fill_progress_indexes(self.data['socket']['current_title'])

      if self.data['socket']['current_status'] == 'Saving to MKV file':
        self.data['socket']['current_progress'][self.data['socket']['current_title']]['buffer'] = 1
        self.data['socket']['current_progress'][self.data['socket']['current_title']]['progress'] = data['current'] / data['max']
      elif self.data['socket']['current_status'] == 'Analyzing seamless segments':
        self.data['socket']['current_progress'][self.data['socket']['current_title']]['buffer'] = data['current'] / data['max']

  def get_progress(self):
    try:
      return {
        "total": {**self.data['socket']['total_progress']},
        "current": {**self.data['socket']['current_progress'][self.data['socket']['current_title']]}
      }
    except Exception:
      return {
        "total": {},
        "current": {}
      }

  def update_status(self, data: ProgressMessageData):
    if data['progress_type'] == 'total':
      self.data['socket']['total_status'] = data['name']
    elif data['progress_type'] == 'current':
      self.data['socket']['current_status'] = data['name']

      if (
        self.data['socket']['current_title'] != None
        and (
          data['name'] == 'Saving to MKV file' 
          or data['name'] == 'Analyzing seamless segments'
        ) and (
          data['index'] > self.data['socket']['current_title']
        )
      ):
        self.data['socket']['current_title'] = data['index']
  
STATE = State()