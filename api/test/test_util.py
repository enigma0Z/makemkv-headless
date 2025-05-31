#!/usr/bin/env python3

import os

import util

from unittest import TestCase
from unittest.mock import MagicMock, patch

multi_response_index = {}

def mock_multi_response(call, response_list):
  multi_response_index[call] = 0
  def fn(*args, **kwargs):
    multi_response_index[call] += 1
    return response_list[multi_response_index[call]-1]

  return fn
  

class UtilTest(TestCase):
  def test_grep(self):
    self.assertTrue(util.grep('foo', ['foo', 'bar', 'baz']), 'Grep returns true if an exact match is present')
    self.assertTrue(util.grep('FOO', ['foo', 'bar', 'baz']), 'Grep returns true if a different-case match is present')
    self.assertTrue(util.grep('FOO', ['barfoobaz', 'bar', 'baz']), 'Grep returns true if a partial text match is present')
    self.assertFalse(util.grep('bin', ['foo', 'bar', 'baz']), 'Grep returns false if no match is present')

  def test_hms_to_seconds(self):
    self.assertEqual(util.hms_to_seconds('1:10:20'), 4220, 'Hours, minutes, and seconds are summed correctly')

  def test_notify(self):
    with patch('subprocess.Popen') as mock_Popen:
      util.notify('foo')
      self.assertEqual(
        mock_Popen.call_args[0][0], 
        ['osascript', '-e', 'display notification "foo" with title "Disc Backup"'], 
        'osascript displays a notification containing the desired message'
      )

  def test_clearing_line(self):
    with patch('shutil.get_terminal_size') as mock_get_terminal_size:
      mock_get_terminal_size.return_value = os.terminal_size((10, 10))
      self.assertEqual(util.clearing_line('x'), 'x' + ' ' * 9, 'A clearing line of terminal width is generated when a string is present')
      self.assertEqual(util.clearing_line(), ' ' * 10, 'A clearing line of terminal width is generated when no string is given')
      self.assertEqual(util.clearing_line(''), ' ' * 10, 'A clearing line of terminal width is generated when an empty string is given')

  def test_rsync(self):
    with (
        patch('subprocess.Popen', autospec=True) as mock_Popen, 
        patch('__main__.open') as mock_open
    ):
      mock_process = MagicMock()
      mock_process.returncode = 0
      mock_interface = MagicMock()
      mock_Popen.return_value = mock_process

      # Happy path
      util.rsync('source', 'dest', interface=mock_interface)

      self.assertEqual(['rsync', '-av', 'source', 'dest'], mock_Popen.mock_calls[1].args[0], 'rsync is called with specified source and destination')

      process_call_list = [f'{call}' for call in mock_process.mock_calls]
      self.assertIn('completed successfully', mock_interface.mock_calls[2].args[0], "rsync completed successfully message is sent")

      # RSync failed
      mock_process.reset_mock()
      mock_interface.reset_mock()
      mock_process.returncode = 1
      util.rsync('source', 'dest', interface=mock_interface)

      self.assertIn('RSYNC FAILED', mock_interface.mock_calls[2].args[0])

  def test_sanitize(self):
    self.assertEqual('foo__bar___baz__', util.sanitize('foo: bar | baz "'), 'Unsafe (non word) filesystem characters are stripped out of the sanitized string')

  def test_string_to_list_int(self):
    self.assertEqual([1,2,3,4,5], util.string_to_list_int('1-5'), 'A dashed range is indexed correctly')  
    self.assertEqual([1,2,3,6,7,8], util.string_to_list_int('1-3,6-8'), 'Multiple dashed ranges parse correctly')
    self.assertEqual([1,3,5], util.string_to_list_int('1,3,5'), 'Comma separated values are indexed correctly')
    self.assertEqual([3,1,5], util.string_to_list_int('3,1,5'), 'The input order is preserved even when nonsequential')

  def test_input_with_default(self):
    with patch('builtins.input') as test_input:
      test_input.return_value = 'response'
      self.assertEqual('response', util.input_with_default('prompt', 'value'), 'The given value overrides the default when given')

      test_input.reset_mock()
      test_input.return_value = ''
      self.assertEqual('value', util.input_with_default('prompt', 'value'), 'The default value is used when no input is provided')

      test_input.reset_mock()
      test_input.return_value = 'none'
      self.assertEqual('', util.input_with_default('prompt', 'value'), 'An empty string is returned for the input value of "none"')

    with patch('builtins.input', mock_multi_response('input', ['', 'response'])) as test_input:
      response = util.input_with_default('prompt')
      self.assertEqual('response', response, 'Input loops until a valid response when validation fails')
