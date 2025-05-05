#!/usr/bin/env python3

import subprocess
from unittest import TestCase
from unittest.mock import DEFAULT, MagicMock, Mock, NonCallableMock, patch

from makemkv import rip_disc

@patch.multiple('subprocess', Popen=DEFAULT)
@patch.multiple('builtins', open=DEFAULT)
@patch.multiple('makemkv', wait_for_disc_inserted=DEFAULT, notify=DEFAULT)
class MakeMKVTest(TestCase):
  def test_rip_disc_default(
      self, 
      Popen: MagicMock, 
      wait_for_disc_inserted: MagicMock, 
      notify: MagicMock,
      open: MagicMock,
  ):

    rip_disc('source', 'dest', interface=MagicMock())

    # Waits for disc to be inserted
    wait_for_disc_inserted.assert_called()

    # Rips all titles if none specified
    self.assertEqual(
      ['--robot', '--progress=-same', 'mkv', 'source', 'all', 'dest'],
      Popen.mock_calls[0].args[0][1:],
      'makemkvcon defaults to all titles when no titles are given'
    )

  def test_rip_disc_makemkv_output_progress(
      self,
      Popen: MagicMock,
      wait_for_disc_inserted: MagicMock,
      notify: MagicMock,
      open: MagicMock,
  ):
    mock_process = NonCallableMock()
    mock_process.stdout = [string.encode() for string in [
      "PRGT:code,id,Total",
      "PRGC:code,id,Current 1",
      "PRGV:0,0,50",
      "PRGV:10,5,50",
      "PRGV:20,10,50",
      "PRGV:30,15,50",
      "PRGV:40,20,50",
      "PRGV:50,25,50",
      "PRGC:code,id,Current 2",
      "PRGV:0,25,50",
      "PRGV:10,30,50",
      "PRGV:20,35,50",
      "PRGV:30,40,50",
      "PRGV:40,45,50",
      "PRGV:50,50,50"
    ]]

    Popen.return_value.__enter__.return_value = mock_process
    mock_interface = MagicMock()
    mock_interface_print = MagicMock()

    mock_interface.print = mock_interface_print

    # Process PRGC, PRGT, PRGV, and MSG lines
    # Calculates current and total percentages
    # Calculates current and total estimated time remaining
    rip_disc('source', 'dest', interface=mock_interface)
    self.assertEqual(15, mock_interface_print.call_count, 'Percentage updates are printed as they are read')


  def test_rip_disk_makemkv_specific_titles(
      self,
      Popen: MagicMock,
      wait_for_disc_inserted: MagicMock,
      notify: MagicMock,
      open: MagicMock,
  ):
    mock_interface = MagicMock()
    mock_interface_print = MagicMock()
    mock_interface.print = mock_interface_print

    rip_disc('source', 'dest', rip_titles=[1, 3, 5], interface=mock_interface)
    self.assertEqual(['1', '3', '5'], [call.args[0][5] for call in Popen.call_args_list], 'Individual titles are ripped')