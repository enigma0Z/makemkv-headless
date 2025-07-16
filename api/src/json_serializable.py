from json import JSONEncoder, dumps

import logging
logger = logging.getLogger(__name__)

class JSONSerializable(JSONEncoder):
  @staticmethod
  def dumps(object: any):
    return dumps(object, cls=JSONSerializable)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def to_json(self):
    '''dumps(self.__dict__, cls=JSONSerializableEncoder)'''

    logger.debug(f'JSONSerializable.to_json({self})')
    return dumps(self, cls=JSONSerializable)

  def json_encoder(self):
    return self.__dict__

  def default(self, object):
    if isinstance(object, JSONSerializable):
      logger.debug(f'isInstance() JSONSerializableEncoder(JSONEncoder).default({object})')
      return object.json_encoder()
    elif is_basic(object) or is_list(object) or is_dict(object): 
      return super().default(object)
    else:
      logger.debug(f'default() else, {object}')
      pass

def is_basic(object):
  return type(object) in [str, int, float, bool, None]

def is_list(object):
  return type(object) == list

def is_dict(object):
  return type(object) == dict