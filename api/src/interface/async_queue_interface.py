#!/usr/bin/env python3

from asyncio import QueueShutDown
from asyncio.queues import Queue

from src.api.socket import SocketConnectionManager
from src.api.state import STATE
from src.interface.base_interface import BaseInterface

from src.models.socket import CurrentProgressMessage, LogMessage, ProgressMessage, ProgressValueMessage, RipStartStopMessage, SocketMessage, TotalProgressMessage

import logging
logger = logging.getLogger(__name__)

PROGRESS_SEND_THRESHOLD = 0.001

class AsyncQueueInterface(BaseInterface):
  def __init__(self, socket: SocketConnectionManager = None):
    self.queue = Queue()
    self.socket = socket

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

  async def send(self, message: SocketMessage):
    if isinstance(message, CurrentProgressMessage) or isinstance(message, TotalProgressMessage):
      await self.queue.put(message)
      STATE.update_status(message)

    elif isinstance(message, ProgressValueMessage):
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
        await self.queue.put(message)

    elif isinstance(message, RipStartStopMessage):
      await self.queue.put(message)
      STATE.socket.current_title = message.index
      STATE.socket.rip_started = message.state == 'start'
    
    else:
      await self.queue.put(message)

    return super().send(message)

  async def print(self, *text, **kwargs):
    sep = kwargs['sep'] if 'sep' in kwargs else ' '
    if 'target' in kwargs and kwargs['target'] != 'status':
      await self.send(LogMessage(message=sep.join(text)))

  async def run(self):
    '''Start the queue processing thread'''
    try:
      while True:
        message = await self.queue.get()
        if (isinstance(message, SocketMessage)):
          self.socket.broadcast(message)
    except QueueShutDown:
      return

INTERFACE = AsyncQueueInterface()