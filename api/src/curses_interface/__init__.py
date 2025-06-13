#!/usr/bin/env python3

import curses
from enum import Enum
import queue
import threading

import logging
logger = logging.getLogger(__name__)

from curses import ascii
from math import floor
from sys import stderr

from src.interface import BaseInterface, Target

KEY_ENTER = 10
KEY_BACKSPACE = 127

CURSES_QUEUE = queue.Queue()
CURSES_OUTPUT_QUEUE = queue.Queue(1)
CURSES_SHUTDOWN = threading.Event()

class Colors(Enum):
  DEFAULT = -1
  TITLE = 1
  ERROR = 2

def curses_queue_thread_fn():
  while not CURSES_SHUTDOWN.is_set():
    try:
      do_response = False
      fn, args, kwargs = CURSES_QUEUE.get(timeout=1/120)
      try:
        if kwargs['_response']:
          do_response=True
          del kwargs['_response']
      except KeyError:
        pass

      if kwargs == {}:
        response = fn(*args)
      else:
        response = fn(*args, **kwargs)
      CURSES_QUEUE.task_done()

      if do_response: CURSES_OUTPUT_QUEUE.put(response)
    except queue.Empty:
      pass

def _curses(fn, *args, **kwargs):
  CURSES_QUEUE.put([fn, args, kwargs])

def _curses_response(fn, *args, **kwargs):
  kwargs['_response'] = True
  CURSES_QUEUE.put([fn, args, kwargs])
  return CURSES_OUTPUT_QUEUE.get()

class WindowRegistry:
  def __init__(self):
    self.windows: dict[str, curses.window] = {}

  def __getattr__(self, name) -> curses.window:
    return self.windows[name]

  def new(self, name, nlines, ncols, begin_y, begin_x):
    self.windows[name] = curses.newwin(nlines, ncols, begin_y, begin_x)
    return self.windows[name]

  def refresh(self):
    for window in self.windows:
      self.windows[window].refresh()

class BorderWindow:
  def __init__(
      self, 
      title: str, 
      height: int, 
      width: int, 
      y: int, 
      x: int, 
      screen: curses.window, 
      scrolling=True
    ):
    self.height = height
    self.scroll_height = height-1
    self.width = width
    self.y = y
    self.x = x
    self.title = title
    self.subtitle = ''
    self.screen = screen

    self.win = screen.subwin(height, width, y, x)
    self.set_title()
  
    if (scrolling):
      self.win.scrollok(True)
      self.win.setscrreg(1, self.scroll_height)

  def set_title(self, title = '', subtitle = '', color=Colors.TITLE.value):
    if (title != ''):
      self.title=title

    if (subtitle != ''):
      self.subtitle=subtitle

    title_str = f'  {self.title} - {self.subtitle}  '
    title_str += ' ' * (self.width - len(title_str))

    _curses(self.win.addstr, 0, 0, title_str, curses.color_pair(color))
    self.refresh()

  def refresh(self):
    _curses(self.win.refresh)

  def print(self, str='', end='\n'):
    if end is None: end = ''
    _curses(self.win.addstr, self.scroll_height, 0, f'{str}{end}')
    _curses(self.win.refresh)

class CursesInterface(BaseInterface):
  def __init__(self):
    self.win = WindowRegistry()
    self.shutdown = threading.Event()

    self.input_queue = queue.Queue(maxsize=1)
    self.output_queue = queue.Queue(maxsize=1)

  def __del__(self):
    self.__exit__()

  def __enter__(self):
    # Curses init
    self.screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.noecho()
    curses.cbreak()
    self.screen.keypad(True)
    self.screen.refresh()

    self.curses_thread = threading.Thread(target=curses_queue_thread_fn)
    self.curses_thread.start()

    self.window_setup()

    self.input_thread = threading.Thread(target=self.input_thread_fn)
    self.input_thread.start()

    return self

  def __exit__(self, *args):
    curses.nocbreak()
    curses.echo()
    curses.endwin()

  def input_thread_fn(self):
    self.screen.refresh()
    self.input_w.refresh()
    height, width = self.input_w.win.getmaxyx()
    try:
      self.input_w.win.nodelay(True)
      while not self.shutdown.is_set():
        prompt = self.input_queue.get()
        input_complete = False
        input_str = ''
        self.print(prompt, target=Target.INPUT, end=None)
        _, start_x = _curses_response(self.input_w.win.getyx)
        while not input_complete:
          k = _curses_response(self.input_w.win.getch)
          if k > -1:
            y, x = _curses_response(self.input_w.win.getyx)
            if (k == KEY_ENTER): # keyboard enter key
              # print(
              #   'enter key', 
              #   'k:', k, 
              #   'height:', height, 
              #   'y:', y, 
              #   'x:', x, 
              #   file=stderr
              # )
              if y == height-1:
                _curses(self.input_w.win.scroll)
                x = start_x 
              else:
                y += 1
                x = start_x 
              input_complete = True
              self.input_queue.task_done()
              self.output_queue.put(input_str)
              input_str = ''

            elif (k == KEY_BACKSPACE): # keyboard backspace key
              # print('backspace, y:', y, 'x:', x, file=stderr)
              input_str = input_str[0:-1]
              if len(input_str) == 0:
                x = start_x
              else:
                x -= 1

              _curses(self.input_w.win.addstr, y, x, ' ')

            elif ascii.isprint(k):
              # print('k:', k, 'y:', y, 'x:', x, file=stderr)
              input_str += chr(k)
              _curses(self.input_w.win.addch, y, x, k)
              x += 1

            # else:
            #   print('Unknown key', k, file=stderr)

            _curses(self.input_w.win.move, y, x)
            _curses(self.input_w.refresh)

    except KeyboardInterrupt as ex:
      self.shutdown.set()
      raise ex

  def window_setup(self):
    # Window set up
    input_section_height = 20
    fg_section_height = int(floor((curses.LINES - 1 - input_section_height) * (2/3)))
    bg_section_height = curses.LINES - 1 - input_section_height - fg_section_height

    self.sort_w = BorderWindow(
      'RSync and Sorting',
      bg_section_height, curses.COLS,
      0, 0,
      self.screen
    )
    self.sort_w.refresh()

    self.mkv_w = BorderWindow(
      'MakeMKVCon',
      fg_section_height, curses.COLS,
      bg_section_height, 0,
      self.screen
    )
    self.mkv_w.refresh()

    self.input_w = BorderWindow(
      'Input',
      input_section_height, curses.COLS,
      fg_section_height + bg_section_height, 0,
      self.screen
    )
    self.input_w.refresh()

    self.refresh()

  def input(self, prompt: str):
    self.input_queue.put(prompt)
    return self.output_queue.get()

  def input_with_default(
      self,
      prompt, 
      value=None,
      validation = lambda v: v != '' and v is not None
    ):
    while True:
      _input = self.input(f'{prompt}\n({value})> ')
      try:
        if _input == '' and value is not None:
          return value
        elif _input.casefold() == 'none':
          return ''
        elif validation(_input):
          return _input
        elif validation(value):
          return value
      except AttributeError:
        self.input_w.print("Error validating input")
        continue

  def refresh(self):
    self.screen.refresh()

  def sanitize_print(self, text, sep, end):
    if text == None: text = []
    text = [str(s) for s in text if s is not None]

    if sep == None: sep = '' 
    else: sep = str(sep)

    if end == None: end = ''
    else: end = str(end)

    return [text, sep, end]

  def get_window(self, target: Target) -> BorderWindow:
    match target:
      case Target.MKV:
        return self.mkv_w
      case Target.SORT: 
        return self.sort_w
      case Target.STATUS: # Deprecated
        return None
      case Target.INPUT:
        return self.input_w
      case _:
        return self.input_w

  def title(
      self,
      *text: list[str],
      target: Target = Target.INPUT,
      sep = ' | ',
  ):
    text, sep, _ = self.sanitize_print(text, sep, None)
    target_window = self.get_window(target)
    if target_window:
      target_window.set_title(subtitle=sep.join(text))

  def print(
      self, 
      *text: list[str], 
      target: str = None, 
      sep=' ', 
      end='\n', 
      **kwargs
  ):
    super().print(text, target=target, sep=sep, end=end)
    if target != 'status':
      text, sep, end = self.sanitize_print(text, sep, end)
      target_window = self.get_window(target)
      if target_window:
        target_window.print(sep.join(text), end=end)

  # Not implemented for curses
  def send(self, message):
    pass

  def get_input(
      self, 
      prompt: str, 
      value: any, 
      validation = lambda v: v != '' and v is not None
    ) -> str:
    return self.input_with_default(prompt, value, validation)