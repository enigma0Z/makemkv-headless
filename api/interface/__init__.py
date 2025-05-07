#!/usr/bin/env python3

from abc import ABC, abstractmethod
from enum import StrEnum, auto, unique
from shutil import get_terminal_size
from typing import Any, Callable

import logging
logger = logging.getLogger(__name__)

from json import dumps, loads

@unique
class Target(StrEnum):
  MKV = auto()
  SORT = auto()
  INPUT = auto()
  STATUS = auto()

class BaseMessage():
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

  def to_json(self):
    return dumps(self.data)

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

class Interface(ABC):
  @abstractmethod
  def __enter__(self, *args, **kwargs):
    return self

  @abstractmethod
  def __exit__(self, *args, **kwargs):
    return self

  @abstractmethod
  def title(
    self, 
    *text: list[str], 
    target: Target = Target.INPUT,
    **kwargs
  ):
    pass

  @abstractmethod
  def print(
    self, 
    *text: list[str], 
    target: Target = Target.INPUT, 
    sep=' ', 
    end='\n', 
    **kwargs
  ):
    logger.debug('interface.print() called with args', {
      'text': text,
      'target': target,
    })

  @abstractmethod
  def send(
      self,
      message: BaseMessage
  ):
    logger.debug('interface.send() message', message)
    pass

  @abstractmethod
  def get_input(
    self, 
    prompt: str,
    value: any,
    validation: Callable[[any], bool]
  ) -> str:
    pass

class PlaintextInterface(Interface):
  def __enter__(self, *args, **kwargs):
    print('enter')
    return super().__enter__(*args)

  def __exit__(self, *args, **kwargs):
    print('exit')
    return super().__exit__(*args)

  def move_cursor_up(self, lines: int):
    print('\033[F'*lines, end=None)

  def title(self, *text, **kwargs): pass # For interface purposes

  def print(
      self, 
      *text, 
      target=Target.INPUT,
      sep=' ', 
      end='\n', 
      **kwargs
  ):
    super().print(*text, target=target, sep=sep, end=end, **kwargs)
    match target:
      # case Target.INPUT: 
      #   self.move_cursor_up(3)
      case Target.MKV:
        self.move_cursor_up(4)
        end += '\n'*3
      case Target.SORT:
        self.move_cursor_up(3)
        end += '\n'*2
      
    print(*text, sep=sep, end=end)

  def send(self, message: BaseMessage):
    super().send(message)
    if type(message) == Message:
      end = ''
      match message.target:
        case Target.MKV:
          self.move_cursor_up(4)
          end += '\n'*3
        case Target.SORT:
          self.move_cursor_up(3)
          end += '\n'*2
      print(message.text, end=end)
    elif type(message) == ProgressMessage:
      print('Progress:', message.to_json())
    else:
      print(message.to_json())

  def get_input(
      self,
      prompt: str, 
      value = None, 
      validation = lambda v: v != '' and v is not None
  ):
    while True:
      _input = input(f'{prompt}\n({value})> ')
      try:
        if _input == '' and value is not None:
          return value
        elif _input.casefold() == 'none':
          return ''
        elif validation(_input):
          return _input
        elif validation(value):
          return value
      except AttributeError:
        print("Error validating input")
        continue
