
#!/usr/bin/env python3

from unittest import TestCase
from unittest.mock import patch
from api.src.interface.message import BaseMessageEvent, MessageEvent, ProgressMessageEvent
from interface import PlaintextInterface, Target

class InterfaceTest(TestCase):
  def test_BaseMessageEvent(self):
    base_message = BaseMessageEvent(target='foo', raw='bar', arbitrary='baz')
    self.assertEqual('foo', base_message.target)
    self.assertEqual('bar', base_message.raw)
    self.assertEqual('baz', base_message.arbitrary)
    self.assertEqual('{"target": "foo", "raw": "bar", "arbitrary": "baz", "type": "BaseMessageEvent"}', base_message.to_json())

    self.assertEqual(base_message.to_json(), BaseMessageEvent.from_json(base_message.to_json()).to_json())
    self.assertEqual(BaseMessageEvent, type(BaseMessageEvent.from_json(base_message.to_json())))

    self.assertEqual(MessageEvent, type(BaseMessageEvent.from_json(MessageEvent('foo', target='bar').to_json())))

  def test_MessageEvent(self):
    self.assertEqual('this is a message\n', MessageEvent('this is a message', target='foo').text)
    self.assertEqual('this is a message\n', MessageEvent('this', 'is', 'a', 'message', target='foo').text)

    with self.assertRaises(AssertionError):
      MessageEvent(target='foo')

  def test_ProgressMessageEvent(self):
    self.assertEqual(10, ProgressMessageEvent(total=10, current=30).total)
    self.assertEqual(30, ProgressMessageEvent(total=10, current=30).current)

    with self.assertRaises(AssertionError):
      ProgressMessageEvent(total=10, target='foo')

    with self.assertRaises(AssertionError):
      ProgressMessageEvent(current=10, target='foo')

  def test_PlaintextInterface(self):
    interface = PlaintextInterface()
    with patch('builtins.print') as mock_print:
      interface.send(MessageEvent('this'))
      self.assertEqual('this\n', mock_print.mock_calls[0].args[0], 'Sending a message without an interface prints it out')

      mock_print.reset_mock()
      interface.send(MessageEvent('test', target=Target.MKV))
      self.assertEqual('\x1b[F'*4, mock_print.mock_calls[0].args[0], 'Printing to MKV backs up four lines')
      self.assertEqual('test\n', mock_print.mock_calls[1].args[0], 'Printing to MKV prints the output')
      self.assertEqual('\n'*3, mock_print.mock_calls[1].kwargs['end'], 'Printing to MKV pads the output with three newlines')

      mock_print.reset_mock()
      interface.send(MessageEvent('test', target=Target.SORT))
      self.assertEqual('\x1b[F'*3, mock_print.mock_calls[0].args[0], 'Printing to sort backs up three lines')
      self.assertEqual('test\n', mock_print.mock_calls[1].args[0], 'Printing to sort prints the output')
      self.assertEqual('\n'*2, mock_print.mock_calls[1].kwargs['end'], 'Printing to sort pads the output with two newlines')