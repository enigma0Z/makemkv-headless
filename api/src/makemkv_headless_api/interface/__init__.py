#!/usr/bin/env python3

from src.interface.base_interface import BaseInterface

_interface: BaseInterface = None

def init_interface(new_interface: BaseInterface):
  global _interface
  _interface = new_interface

def get_interface():
  return _interface