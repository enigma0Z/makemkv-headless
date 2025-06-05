#!/usr/bin/env python3

from queue import Queue
from re import match
from interface.message import Message
from interface import BaseInterface

class ThreadQueueInterface(BaseInterface):
  def __init__(self):
    self.queue = Queue()

  def __enter__(self, *args, **kwargs):
    '''Not implemented'''
    pass

  def __exit__(self, *args, **kwargs):
    '''Not implemented'''
    pass

  def title( self, *args, **kwargs):
    '''Not implemented'''
    pass

  def get_input(self, *args, **kwargs) -> str:
    '''Not implemented'''
    pass

  def send(self, message):
    self.queue.put(message)
    return super().send(message)

  def print(self, *text, **kwargs):
    if 'target' in kwargs and kwargs['target'] == 'mkv' and len(text) == 1:
      if (text[0].startswith("MSG")):
        message_text = match(r'.+?,"(.+?)".*', text[0]).groups()[0]
        self.send(Message(message_text, **kwargs, end=''))
        return 

    self.send(Message(*text, **kwargs, end=''))
