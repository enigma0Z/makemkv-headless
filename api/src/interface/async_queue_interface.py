#!/usr/bin/env python3

from asyncio import QueueShutDown
from asyncio.queues import Queue

from src.api.state import STATE
from src.interface.base_interface import BaseInterface
from src.message.base_message_event import BaseMessageEvent
from src.message.message_event import MessageEvent
from src.message.progress_message_event import ProgressMessageEvent
from src.message.progress_value_message_event import ProgressValueMessageEvent
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent

import logging
logger = logging.getLogger(__name__)

PROGRESS_SEND_THRESHOLD = 0.001

class AsyncQueueInterface(BaseInterface):
  def __init__(self, socket: None = None):
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

  async def send(self, message: BaseMessageEvent):
    if isinstance(message, ProgressMessageEvent):
      await self.queue.put(message)
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
        await self.queue.put(message)

    elif isinstance(message, RipStartStopMessageEvent):
      await self.queue.put(message)
      STATE.data['socket']['current_title'] = message.data['index']
      STATE.data['socket']['rip_started'] = message.data['state'] == 'start'
    
    else:
      await self.queue.put(message)

    return super().send(message)

  async def print(self, *text, **kwargs):
    if 'target' in kwargs and kwargs['target'] != 'status':
      await self.send(MessageEvent(*text, **kwargs))

  async def run(self):
    '''Start the queue processing thread'''
    try:
      while True:
        message = await self.queue.get()
        if type(message) != BaseMessageEvent:
          logger.debug(f'sending message: {message}')
          # self.socket.emit(message.type, message.data)
        else:
          logger.debug(f'skipping message: {message}')
    except QueueShutDown:
      return

INTERFACE = AsyncQueueInterface()