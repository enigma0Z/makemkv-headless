from abc import abstractmethod
from threading import Event, Thread


class StoppableThread(Thread):
  def __init__(self, *args, **kwargs):
    assert 'target' not in kwargs
    super().__init__(*args, **kwargs)
    self._args = kwargs['args'] if 'args' in kwargs else []
    self._kwargs = kwargs['kwargs'] if 'kwargs' in kwargs else {}
    self._started_event = Event()
    self._stop_event = Event()

  @abstractmethod
  def __call__(self, *args, **kwargs):
    return NotImplemented

  def _run_target(self):
    self(*self._args, **self._kwargs)

  def run(self):
    try:
      self._started_event.set()
      self._run_target()
    finally:
      self._started_event.clear()

  def stop(self):
    self._stop_event.set()

  def started(self):
    return self._started_event.is_set()

  def stop_requested(self):
    return self._stop_event.is_set()