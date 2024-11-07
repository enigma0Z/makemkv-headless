#!/usr/bin/env python3

from abc import ABC, abstractmethod
from shutil import get_terminal_size
from typing import Callable

class Interface(ABC):
  @abstractmethod
  def __enter__(self, *args):
    return self

  @abstractmethod
  def __exit__(self, *args):
    return self

  @abstractmethod
  def print_sort(self, *text: list[str], sep=' ', end='\n'):
    pass

  @abstractmethod
  def print_mkv(self, *text: list[str], sep=' ', end='\n'):
    pass

  @abstractmethod
  def print_status(self, *text: list[str], sep=' ', end='\n'):
    pass

  @abstractmethod
  def print_input(self, *text: list[str], sep=' ', end='\n'):
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
  def __enter__(self, *args):
    return super().__enter__(*args)

  def __exit__(self, *args):
    return super().__exit__(*args)

  def move_cursor_up(self, lines: int):
    print('\033[F'*lines, end=None)

  def clearing_line(self, line=''):
    return line + ' ' * (-len(line) % get_terminal_size().columns)

  def print_status(self, *text, sep=' ', end='\n'):
    self.move_cursor_up(3)
    print(text, sep=sep, end=end)

  def print_sort(self, *text, sep=' ', end='\n'):
    self.move_cursor_up(4)
    print(text, sep=sep, end=end)

  def print_mkv(self, *text, sep=' ', end='\n'):
    self.print_sort(*text, sep, end)

  def print_input(self, *text, sep=' ', end='\n'):
    self.print_sort(*text, sep, end)

  def get_input(
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
