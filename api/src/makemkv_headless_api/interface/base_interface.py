
from abc import ABC, abstractmethod
from typing import Callable

import logging

from src.interface.target import Target
from src.message.base_message_event import BaseMessageEvent
logger = logging.getLogger(__name__)

class BaseInterface(ABC):
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
    logger.debug(' '.join([
      'interface.print() called with args', 
      f'text: {text}',
      f'target: {target}',
    ]))

  @abstractmethod
  def send(
      self,
      message: BaseMessageEvent
  ):
    # logger.debug('interface.send() message', message)
    pass

  @abstractmethod
  def get_input(
    self, 
    prompt: str,
    value: any,
    validation: Callable[[any], bool]
  ) -> str:
    pass