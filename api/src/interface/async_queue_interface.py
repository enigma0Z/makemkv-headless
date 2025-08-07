#!/usr/bin/env python3

from asyncio import QueueShutDown, create_task
from asyncio.queues import Queue

from src.api.socket import SocketConnectionManager
from src.api.state import STATE
from src.interface.base_interface import BaseInterface

from src.interface.target import Target
from src.models.makemkv import from_raw
from src.models.socket import CurrentProgressMessage, LogMessage, ProgressMessage, ProgressValueMessage, RipStartStopMessage, SocketMessage, TotalProgressMessage, mkv_message_from_raw

import logging
logger = logging.getLogger(__name__)

PROGRESS_SEND_THRESHOLD = 0.001

Target.MKV

class AsyncQueueInterface(BaseInterface):
  def __init__(self, socket: SocketConnectionManager = None):
    self.queue = Queue()
    self.socket = socket
    logger.debug(f'Initializing {self.__class__.__name__} with socket {socket}')

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

  def send(self, message: SocketMessage):
    return create_task(self._send(message))

  async def _send(self, message: SocketMessage):
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
      logger.info(message)

    return super().send(message)

  def print(self, *text, sep=' ', target: Target=Target.INPUT, **kwargs):
    match target:
      case Target.MKV:
        self.send(mkv_message_from_raw(sep.join(text)))
      case Target.INPUT | Target.SORT:
        self.send(LogMessage(message=sep.join(text)))
      case Target.STATUS:
        pass


  async def run(self):
    '''Start the queue processing thread'''
    try:
      while True:
        message = await self.queue.get()
        if (isinstance(message, SocketMessage)):
          await self.socket.broadcast(message)
    except QueueShutDown:
      return

INTERFACE = AsyncQueueInterface()