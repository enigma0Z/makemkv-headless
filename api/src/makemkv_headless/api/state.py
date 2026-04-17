import logging
from typing import TypedDict

from makemkv_headless.models.socket import CurrentProgressMessage, ProgressValueMessage, TotalProgressMessage
from makemkv_headless.models.state import ProgressStateModel, StateModel

logger = logging.getLogger(__name__)

class State(StateModel):
  def json_encoder(self):
    return self.data

  def reset_all(self): 
    for field, field_info in State.model_fields.items():
      if field_info.default_factory:
        default_value = field_info.default_factory()
      else:
        default_value = field_info.default
      
      setattr(self, field, default_value)

    self.model_fields_set.clear()

  def reset_socket(self):
    for field, field_info in type(self.socket.rip).model_fields.items():
      if field_info.default_factory:
        default_value = field_info.default_factory()
      else:
        default_value = field_info.default

      setattr(self.socket.rip, field, default_value)

  def reset_rip_indexes(self):
    self.rip.sort_info.main_indexes = []
    self.rip.sort_info.extra_indexes = []

  def fill_progress_indexes(self, index):
    if len(self.socket.rip.current_progress) <= index:
      # Create empty current_progress entries as needed
      self.socket.rip.current_progress = [ 
        self.socket.rip.current_progress[index] 
        if len(self.socket.rip.current_progress) > index
        else ProgressStateModel()
        for index in range(0, index+1)
      ]
    pass

  def update_progress(self, data: ProgressValueMessage):
    self.socket.rip.total_progress.progress = data.total / data.max
    if (self.socket.rip.current_title != None):
      self.fill_progress_indexes(self.socket.rip.current_title)

      if self.socket.rip.current_status == 'Saving to MKV file':
        self.socket.rip.current_progress[self.socket.rip.current_title].buffer = 1
        self.socket.rip.current_progress[self.socket.rip.current_title].progress = data.current / data.max
      elif self.socket.rip.current_status == 'Analyzing seamless segments':
        self.socket.rip.current_progress[self.socket.rip.current_title].buffer = data.current / data.max

  class ProgressResponse(TypedDict):
    total: ProgressStateModel | None
    current: ProgressStateModel

  def get_progress(self) -> ProgressResponse:
    try:
      return {
        "total": self.socket.rip.total_progress,
        "current": self.socket.rip.current_progress[self.socket.rip.current_title]
      }
    except Exception:
      return {
        "total": None,
        "current": None,
      }

  def update_status(self, data: CurrentProgressMessage | TotalProgressMessage):
    if isinstance(data, TotalProgressMessage):
      self.socket.rip.total_status = data.name
    if isinstance(data, CurrentProgressMessage):
      self.socket.rip.current_status = data.name

      if (
        self.socket.rip.current_title != None
        and (
          data.name == 'Saving to MKV file' 
          or data.name == 'Analyzing seamless segments'
        ) and (
          data.index > self.socket.rip.current_title
        )
      ):
        self.socket.rip.current_title = data.index
  
STATE = State()