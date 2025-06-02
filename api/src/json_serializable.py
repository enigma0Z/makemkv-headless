from functools import wraps
from json import JSONEncoder, dumps
from typing import Callable
from flask import Response

class JSONSerializable:
  def to_json(self):
    return dumps(self.__dict__, cls=JSONSerializableEncoder)

class JSONSerializableEncoder(JSONEncoder):
  def default(self, object: JSONSerializable):
    if is_basic(object): 
      return super().default(object)
    elif is_list(object):
      return dumps([o.__dict__ for o in object])
    elif hasattr(object, 'to_json'): 
      return object.__dict__
    else:
      pass

def is_basic(object):
  return type(object) in [str, int, float, bool, None]

def is_list(object):
  return type(object) == list