from re import match
from src.message.base_message_event import BaseMessageEvent


class MessageEvent(BaseMessageEvent):
  def __init__(self, *text, sep=' ', end="\n", **data):
    super().__init__(**data)
    try:
      if len(text) > 0:
        assert "text" not in data
        self.data['text'] = sep.join([ str(item) for item in text ]) + end
      else:
        self.data['text'] = match(r'.+?,"(.+?)".*', data['raw']).groups()[0]
    except Exception as ex:
      self.data['text'] = str(ex)