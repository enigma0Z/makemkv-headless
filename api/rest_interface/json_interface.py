#!/usr/bin/env python3

from typing import Callable
from ..interface import Interface, Target

class JsonInterface(Interface):
  def title(
      self,
      *text: list[str],
      target: Target = Target.INPUT,
      **kwargs
  ):
    pass

  def print(
      self,
      *text: list[str],
      target: Target = Target.INPUT,
      **kwargs
  ):
    pass

  def get_input(
    self,
    prompt: str,
    value: any,
    validation: Callable[[any], bool]
  ) -> str:
    pass