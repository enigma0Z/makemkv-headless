from json import loads

from json_serializable import JSONSerializable

class BaseMessage(JSONSerializable):
  @staticmethod
  def from_json(json_str: str):
    data = loads(json_str)
    match data['type']:
      case 'Message':
        return Message(**data)
      case 'ProgressMessage':
        return ProgressMessage(**data)
      case _:
        return BaseMessage(**data)

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

class Message(BaseMessage):
  def __init__(self, *text, sep=' ', end="\n", **data):
    if len(text) > 0:
      assert "text" not in data
      data['text'] = sep.join(text) + end
    else:
      assert "text" in data

    super().__init__(**data)
    
class ProgressMessage(BaseMessage):
  def __init__(self, **data):
    assert "total" in data
    assert "current" in data
    super().__init__(**data)
