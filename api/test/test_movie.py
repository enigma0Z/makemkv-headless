#!/usr/bin/env python3

from argparse import Namespace
from unittest import TestCase
from unittest.mock import DEFAULT, MagicMock, Mock, patch

from rip import rip_titles
from sort import SortInfo
from test.data.toc_test_data import generate_CINFO, generate_SINFO, generate_TINFO
from toc import TOC

@patch.multiple('builtins', open=DEFAULT)
@patch.multiple('os', makedirs=DEFAULT, rename=DEFAULT)
@patch.multiple('shutil', rmtree=DEFAULT)
@patch.multiple('tempfile', mkdtemp=DEFAULT)
@patch.multiple('sys', exit=DEFAULT)
@patch.multiple(
  'rip', 
  sort_titles=DEFAULT,
  eject_disc=DEFAULT, 
  rip_disc=DEFAULT,
)
class MovieTest(TestCase):
  def test_rip_movie(self, *args, **kwargs: dict[str, MagicMock]):
    # Type hints don't work for kwargs I guess.
    mock: dict[str, MagicMock] = kwargs

    mock['mkdtemp'].return_value = 'temp_dir'

    mock_toc = TOC()
    mock_toc.get_from_list(
      generate_CINFO() + 
      generate_TINFO() + 
      generate_SINFO() +
      generate_TINFO(title_index=1) + 
      generate_SINFO(title_index=1) +
      generate_TINFO(title_index=2) + 
      generate_SINFO(title_index=2)
    )

    mock_interface = MagicMock()

    mock_sort_info=SortInfo('movie name unsanitary', 'movie_id', [0], [1,2]),

    rip_titles(
      'source', 'dest',
      toc=mock_toc,
      sort_info=SortInfo('movie name unsanitary', 'movie_id', [0], [1,2]),
      interface=mock_interface
    )

    # Temporary directory is created
    mock['mkdtemp'].assert_called_once()

    # Rip path is sanitized and contains the given ID (default tmdb)
    mock['makedirs'].assert_called_once()
    self.assertEqual('temp_dir/movie_name_unsanitary [tmdbid-movie_id]/extras', mock['makedirs'].call_args_list[0].args[0])

    # mkmkvcon log file is opened and written to
    mock['open'].assert_called_once()
    self.assertEqual('temp_dir/movie_name_unsanitary [tmdbid-movie_id]/name1-makemkvcon.txt', mock['open'].call_args.args[0])

    # rip_disc is called twice, once for mains once for extras
    self.assertEqual(2, mock['rip_disc'].call_count)
    self.assertEqual(('source', 'temp_dir/movie_name_unsanitary [tmdbid-movie_id]'), mock['rip_disc'].call_args_list[0].args)
    self.assertEqual([0], mock['rip_disc'].call_args_list[0].kwargs['rip_titles'])

    self.assertEqual(('source', 'temp_dir/movie_name_unsanitary [tmdbid-movie_id]'), mock['rip_disc'].call_args_list[1].args)
    self.assertEqual([1,2], mock['rip_disc'].call_args_list[1].kwargs['rip_titles'])

    mock['sort_titles'].assert_called_once()