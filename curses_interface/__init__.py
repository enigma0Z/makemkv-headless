#!/usr/bin/env python3

import curses
import queue
import threading

from curses import ascii
from math import floor
from sys import stderr

from interface import Interface

KEY_ENTER = 10
KEY_BACKSPACE = 127

CURSES_QUEUE = queue.Queue()
CURSES_OUTPUT_QUEUE = queue.Queue(1)
CURSES_SHUTDOWN = threading.Event()

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

      # print('FN received', fn, args, kwargs, file=stderr)
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
  def __init__(self, title, height, width, y, x, screen, scrolling=True):
    self.height = height
    self.scroll_height = height-3
    self.width = width
    self.y = y
    self.x = x
    self.title = title
    self.screen = screen
    
    self.b_win = curses.newwin(
      height, width, y, x
    )

    self.win = self.b_win.subwin(height-2, width-4, y+1, x+2)

    self.b_win.border()
    self.b_win.addstr(0, 2, f' {title} ')

    if (scrolling):
      self.win.scrollok(True)
      self.win.setscrreg(0, self.scroll_height)

  def refresh(self):
    # self.screen.refresh()
    # self.b_win.refresh()
    # self.win.refresh()
    _curses(self.b_win.refresh)
    _curses(self.win.refresh)

  def print(self, str='', end='\n'):
    if end is None: end = ''
    _curses(self.win.addstr, self.scroll_height, 0, f'{str}{end}')
    _curses(self.win.refresh)
    # self.win.addstr(self.scroll_height, 0, f'{str}{end}')
    # self.win.refresh()

class CursesInterface(Interface):
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
    curses.noecho()
    curses.cbreak()
    self.screen.keypad(True)
    self.screen.refresh()
    self.window_setup()

    try:
      self.input_thread = threading.Thread(target=self.input_thread_fn)
      self.input_thread.start()
      self.curses_thread = threading.Thread(target=curses_queue_thread_fn)
      self.curses_thread.start()

    except KeyboardInterrupt:
      self.shutdown.set()

    return self

  def __exit__(self, *args):
    self.screen.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    # print('Succesfully cleaned up curses')

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
        self.print_input(prompt, end=None)
        _, start_x = self.input_w.win.getyx()
        while not input_complete:
          k = _curses_response(self.input_w.win.getch)
          if k > -1:
            y, x = _curses_response(self.input_w.win.getyx)
            if (k == KEY_ENTER): # keyboard enter key
              print(
                'enter key', 
                'k:', k, 
                'height:', height, 
                'y:', y, 
                'x:', x, 
                file=stderr
              )
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
              print('backspace, y:', y, 'x:', x, file=stderr)
              input_str = input_str[0:-1]
              if len(input_str) == 0:
                x = start_x
              else:
                x -= 1

              _curses(self.input_w.win.addstr, y, x, ' ')

            elif ascii.isprint(k):
              print('k:', k, 'y:', y, 'x:', x, file=stderr)
              input_str += chr(k)
              _curses(self.input_w.win.addch, y, x, k)
              x += 1

            else:
              print('Unknown key', k, file=stderr)

            # print('k:', k, 'y:', y, 'x:', x, file=stderr)
            _curses(self.input_w.win.move, y, x)
            _curses(self.input_w.refresh)

    except KeyboardInterrupt as ex:
      self.shutdown.set()
      raise ex

  def window_setup(self):
    # Window set up
    input_section_height = 20
    status_section_height = 5
    fg_section_height = int(floor((curses.LINES - 1 - status_section_height - input_section_height) * (1/2)))
    bg_section_height = curses.LINES - 1 - input_section_height - status_section_height - fg_section_height
    # task_section_width = int(floor(curses.COLS) / 4)
    # bg_section_width = curses.COLS - task_section_width

    self.sort_w = BorderWindow(
      'RSync and Sorting',
      bg_section_height, curses.COLS,
      0, 0,
      self.screen
    )
    self.sort_w.refresh()

    # self.task_w = BorderWindow(
    #   'Tasks',
    #   bg_section_height, task_section_width,
    #   0, bg_section_width,
    #   self.screen
    # )
    # self.task_w.refresh()

    self.mkv_w = BorderWindow(
      'MakeMKVCon',
      fg_section_height, curses.COLS,
      bg_section_height, 0,
      self.screen
    )
    self.mkv_w.refresh()

    self.status_w = BorderWindow(
      'Status',
      status_section_height, curses.COLS,
      fg_section_height + bg_section_height, 0,
      self.screen,
    )
    self.status_w.refresh()

    self.input_w = BorderWindow(
      'Input',
      input_section_height, curses.COLS,
      fg_section_height + bg_section_height + status_section_height, 0,
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

  def print_status(self, *text: list[str], sep=' ', end='\n'):
    text, sep, end = self.sanitize_print(text, sep, end)
    self.status_w.print(sep.join(text), end=end)

  def print_mkv(self, *text: list[str], sep=' ', end='\n'):
    text, sep, end = self.sanitize_print(text, sep, end)
    self.mkv_w.print(sep.join(text), end=end)

  def print_input(self, *text: list[str], sep=' ', end='\n'):
    text, sep, end = self.sanitize_print(text, sep, end)
    self.input_w.print(sep.join([s if s is not None else '' for s in text]), end=end)

  def print_sort(self, *text: list[str], sep=' ', end='\n'):
    text, sep, end = self.sanitize_print(text, sep, end)
    self.sort_w.print(sep.join(text), end=end)

  def get_input(
      self, 
      prompt: str, 
      value: any, 
      validation = lambda v: v != '' and v is not None
    ) -> str:
    return self.input_with_default(prompt, value, validation)