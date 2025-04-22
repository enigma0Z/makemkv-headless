#!/usr/bin/env python3

from abc import ABC, abstractmethod
from enum import StrEnum, auto, unique
from shutil import get_terminal_size
from typing import Any, Callable

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
    return BaseMessage(**loads(json_str))

  def __init__(self, **data):
    assert "target" in data
    self.data = data
    self.data['type'] = type(self).__name__

  def __setattr__(self, name, value):
    self.data[name] = value

  def __getattr__(self, name):
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

  def clearing_line(self, line=''):
    return line + ' ' * (-len(line) % get_terminal_size().columns)

  def title(self, *text, **kwargs): pass # For interface purposes

  def print(
      self, 
      message: BaseMessage
  ):
    if message.sep == None: message.sep = ' '
    if message.end == None: message.end = '\n'

    match message.target:
      # case Target.INPUT: 
      #   self.move_cursor_up(3)
      case Target.MKV:
        self.move_cursor_up(4)
        end += '\n'*3
      case Target.SORT:
        self.move_cursor_up(3)
        end += '\n'*2
      
    print(message.text, sep=message.sep, end=message.end)
  
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
