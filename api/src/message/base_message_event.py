from src.json_serializable import JSONSerializable


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

  def __repr__(self):
    return f'{type(self)} {self.data}'

  def __str__(self):
    return f'{self.data}'