
#!/usr/bin/env python3

from unittest import TestCase
from unittest.mock import patch
from api.src.interface.message import BaseMessage, Message, ProgressMessage
from interface import PlaintextInterface, Target

class InterfaceTest(TestCase):
  def test_BaseMessage(self):
    base_message = BaseMessage(target='foo', raw='bar', arbitrary='baz')
    self.assertEqual('foo', base_message.target)
    self.assertEqual('bar', base_message.raw)
    self.assertEqual('baz', base_message.arbitrary)
    self.assertEqual('{"target": "foo", "raw": "bar", "arbitrary": "baz", "type": "BaseMessage"}', base_message.to_json())

    self.assertEqual(base_message.to_json(), BaseMessage.from_json(base_message.to_json()).to_json())
    self.assertEqual(BaseMessage, type(BaseMessage.from_json(base_message.to_json())))

    self.assertEqual(Message, type(BaseMessage.from_json(Message('foo', target='bar').to_json())))

  def test_Message(self):
    self.assertEqual('this is a message\n', Message('this is a message', target='foo').text)
    self.assertEqual('this is a message\n', Message('this', 'is', 'a', 'message', target='foo').text)

    with self.assertRaises(AssertionError):
      Message(target='foo')

  def test_ProgressMessage(self):
    self.assertEqual(10, ProgressMessage(total=10, current=30).total)
    self.assertEqual(30, ProgressMessage(total=10, current=30).current)

    with self.assertRaises(AssertionError):
      ProgressMessage(total=10, target='foo')

    with self.assertRaises(AssertionError):
      ProgressMessage(current=10, target='foo')

  def test_PlaintextInterface(self):
    interface = PlaintextInterface()
    with patch('builtins.print') as mock_print:
      interface.send(Message('this'))
      self.assertEqual('this\n', mock_print.mock_calls[0].args[0], 'Sending a message without an interface prints it out')

      mock_print.reset_mock()
      interface.send(Message('test', target=Target.MKV))
      self.assertEqual('\x1b[F'*4, mock_print.mock_calls[0].args[0], 'Printing to MKV backs up four lines')
      self.assertEqual('test\n', mock_print.mock_calls[1].args[0], 'Printing to MKV prints the output')
      self.assertEqual('\n'*3, mock_print.mock_calls[1].kwargs['end'], 'Printing to MKV pads the output with three newlines')

      mock_print.reset_mock()
      interface.send(Message('test', target=Target.SORT))
      self.assertEqual('\x1b[F'*3, mock_print.mock_calls[0].args[0], 'Printing to sort backs up three lines')
      self.assertEqual('test\n', mock_print.mock_calls[1].args[0], 'Printing to sort prints the output')
      self.assertEqual('\n'*2, mock_print.mock_calls[1].kwargs['end'], 'Printing to sort pads the output with two newlines')