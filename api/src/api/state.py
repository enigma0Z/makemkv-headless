import logging
from typing import TypedDict

from src.models.socket import CurrentProgressMessage, ProgressValueMessage, TotalProgressMessage
from src.models.state import ProgressStateModel, StateModel

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
    for field, field_info in type(self.socket).model_fields.items():
      if field_info.default_factory:
        default_value = field_info.default_factory()
      else:
        default_value = field_info.default

      setattr(self.socket, field, default_value)

  def fill_progress_indexes(self, index):
    if len(self.socket.current_progress) <= index:
      # Create empty current_progress entries as needed
      self.socket.current_progress = [ 
        self.socket.current_progress[index] 
        if len(self.socket.current_progress) > index
        else ProgressStateModel()
        for index in range(0, index+1)
      ]
    pass

  def update_progress(self, data: ProgressValueMessage):
    self.socket.total_progress.progress = data.total / data.max
    if (self.socket.current_title != None):
      self.fill_progress_indexes(self.socket.current_title)

      if self.socket.current_status == 'Saving to MKV file':
        self.socket.current_progress[self.socket.current_title].buffer = 1
        self.socket.current_progress[self.socket.current_title].progress = data.current / data.max
      elif self.socket.current_status == 'Analyzing seamless segments':
        self.socket.current_progress[self.socket.current_title].buffer = data.current / data.max

  class ProgressResponse(TypedDict):
    total: ProgressStateModel | None
    current: ProgressStateModel

  def get_progress(self) -> ProgressResponse:
    try:
      return {
        "total": self.socket.total_progress,
        "current": self.socket.current_progress[self.socket.current_title]
      }
    except Exception:
      return {
        "total": None,
        "current": None,
      }

  def update_status(self, data: CurrentProgressMessage | TotalProgressMessage):
    if isinstance(data, TotalProgressMessage):
      self.socket.total_status = data.name
    if isinstance(data, CurrentProgressMessage):
      self.data.socket.current_status = data.name

      if (
        self.socket.current_title != None
        and (
          data.name == 'Saving to MKV file' 
          or data.name == 'Analyzing seamless segments'
        ) and (
          data.index > self.socket.current_title
        )
      ):
        self.socket.current_title = data.index
  
STATE = State()