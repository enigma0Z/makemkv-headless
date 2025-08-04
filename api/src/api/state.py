import logging

from src.message.progress_message_event import ProgressMessageData
from src.message.progress_value_message_event import ProgressValueMessageData
from src.models.state import StateModel

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