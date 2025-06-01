#!/usr/bin/env python3

from queue import Queue
from threading import Lock
from typing import Callable
from interface import Interface, Target, Message

class ThreadQueueInterface(Interface):
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
    self.send(Message(*text, **kwargs))
