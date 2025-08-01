#!/usr/bin/env python3

import logging
from queue import Empty, Queue
from threading import Thread

# from gevent.queue import Empty, Queue
# from gevent.threading import Thread

from flask_socketio import SocketIO
from src.api.flask.singletons.state import STATE
from src.interface.base_interface import BaseInterface
from src.message.base_message_event import BaseMessageEvent
from src.message.message_event import MessageEvent
from src.message.progress_message_event import ProgressMessageEvent
from src.message.progress_value_message_event import ProgressValueMessageEvent
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent

logger = logging.getLogger(__name__)

PROGRESS_SEND_THRESHOLD = 0.001

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
    if isinstance(message, ProgressMessageEvent):
      self.queue.put(message)
      STATE.update_status(message.data)

    elif isinstance(message, ProgressValueMessageEvent):
      progress_before = STATE.get_progress()
      STATE.update_progress(message.data)
      progress_after = STATE.get_progress()

      send_update = True

      outer_keys = ['total', 'current']
      inner_keys = ['buffer', 'progress']

      try:
        for outer_key in outer_keys:
          for inner_key in inner_keys:
            if (
              outer_key in progress_before
              and outer_key in progress_after
            ):
              if (
                inner_key in progress_before[outer_key]
                and inner_key in progress_after[outer_key]
              ):
                if (
                  isinstance(progress_before[outer_key][inner_key], float)
                  and isinstance(progress_after[outer_key][inner_key], float)
                ):
                  if (
                    progress_after[outer_key][inner_key] - progress_before[outer_key][inner_key] > PROGRESS_SEND_THRESHOLD
                  ): # Buffer or Progress have progress over threshold
                    send_update = True
              else: # Total/Current don't both have Buffer/Progress
                send_update = True
            else: # Before/After Don't both have Total/Current
              send_update = True
      except Exception as ex:
        logger.error(ex)
        send_update = True

      if (send_update): 
        self.queue.put(message)


    elif isinstance(message, RipStartStopMessageEvent):
      self.queue.put(message)
      STATE.data['socket']['current_title'] = message.data['index']
      STATE.data['socket']['rip_started'] = message.data['state'] == 'start'
    
    else:
      self.queue.put(message)

    return super().send(message)

  def print(self, *text, **kwargs):
    if 'target' in kwargs and kwargs['target'] != 'status':
      self.send(MessageEvent(*text, **kwargs))

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
      if type(message) != BaseMessageEvent:
        logger.debug(f'sending message: {message}')
        self.socket.emit(message.type, message.data)
      else:
        logger.debug(f'skipping message: {message}')