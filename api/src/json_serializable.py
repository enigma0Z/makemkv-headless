from functools import wraps
from json import JSONEncoder, dumps
from typing import Callable
from flask import Response

import logging
logger = logging.getLogger(__name__)

class JSONSerializable:
  def to_json(self):
    '''dumps(self.__dict__, cls=JSONSerializableEncoder)'''

    logger.debug(f'JSONSerializable.to_json({self})')
    return dumps(self.__dict__, cls=JSONSerializableEncoder)

  def json_encoder(self):
    return self.__dict__

class JSONSerializableEncoder(JSONEncoder):
  def default(self, object: JSONSerializable):
    logger.debug(f'JSONSerializableEncoder(JSONEncoder).default({object})')
    if isinstance(object, JSONSerializable):
      return object.json_encoder()
    elif is_basic(object) or is_list(object) or is_dict(object): 
      return super().default(object)
    else:
      pass

def is_basic(object):
  return type(object) in [str, int, float, bool, None]

def is_list(object):
  return type(object) == list

def is_dict(object):
  return type(object) == dict