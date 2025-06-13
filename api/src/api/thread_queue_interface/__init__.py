#!/usr/bin/env python3

import logging
from queue import Queue
from threading import Thread

from flask_socketio import SocketIO
from src.api.singletons.state import STATE

from src.interface import BaseInterface
from src.interface.message import BaseMessageEvent, MessageEvent, ProgressMessageEvent, ProgressValueMessageEvent, RipStartStopMessageEvent, build_message

logger = logging.getLogger(__name__)

class ThreadQueueInterface(BaseInterface):
  def __init__(self, socket: SocketIO = None):
    self.queue = Queue()
    self.socket = socket
    self.thread = Thread(
      target=self.thread_target,
      daemon=True
    )

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
    message_data = {**kwargs, "raw": ' '.join(text)}
    self.send(build_message(**message_data))

  def run(self):
    '''Start the queue processing thread'''
    if (self.socket != None):
      logger.info('Starting socket queue thread')
      self.thread.start()
    else:
      raise ValueError("Socket has not been initialized")

  def thread_target(self):
    while True:
      message = self.queue.get()
      if isinstance(message, BaseMessageEvent):
        self.socket.emit(message.type, message.data)