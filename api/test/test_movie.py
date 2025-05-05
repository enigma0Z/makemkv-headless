#!/usr/bin/env python3

from argparse import Namespace
from unittest import TestCase
from unittest.mock import DEFAULT, MagicMock, Mock, patch

from movie import rip_movie, rip_movie_interactive
from test.data.toc_test_data import generate_CINFO, generate_SINFO, generate_TINFO
from toc import TOC

@patch.multiple('builtins', open=DEFAULT)
@patch.multiple('os', makedirs=DEFAULT, rename=DEFAULT)
@patch.multiple('shutil', rmtree=DEFAULT)
@patch.multiple('tempfile', mkdtemp=DEFAULT)
@patch.multiple('sys', exit=DEFAULT)
@patch.multiple(
  'movie', 
  eject_disc=DEFAULT, 
  wait_for_disc_inserted=DEFAULT, 
  # sanitize=DEFAULT,
  rip_disc=DEFAULT,
  # hms_to_seconds=DEFAULT
  rsync=DEFAULT
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

    rip_movie(
      'source', 'dest',
      toc=mock_toc,
      main_indexes=[0],
      extras_indexes=[1,2],
      movie_name='movie_name unsanitary',
      id='movie_id',
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

    # Files are renamed (os.rename) to the right paths
    self.assertEqual(3, mock['rename'].call_count) # Once per title
    self.assertEqual(
      (
        'temp_dir/movie_name_unsanitary [tmdbid-movie_id]/filename.mkv', 
        'temp_dir/movie_name_unsanitary [tmdbid-movie_id]/movie_name_unsanitary [tmdbid-movie_id] - 0.mkv'
      ), 
      mock['rename'].call_args_list[0].args
    )
    self.assertEqual(
      (
        'temp_dir/movie_name_unsanitary [tmdbid-movie_id]/filename.mkv', 
        'temp_dir/movie_name_unsanitary [tmdbid-movie_id]/extras/filename.mkv'
      ), 
      mock['rename'].call_args_list[1].args
    )
    self.assertEqual(
      (
        'temp_dir/movie_name_unsanitary [tmdbid-movie_id]/filename.mkv', 
        'temp_dir/movie_name_unsanitary [tmdbid-movie_id]/extras/filename.mkv'
      ), 
      mock['rename'].call_args_list[2].args
    )

    # Files are rsync'ed to the destination
    mock['rsync'].assert_called_once()

    # Files are cleaned up
    mock['rmtree'].assert_called_once()

    # The disc is ejected
    mock['eject_disc'].assert_called_once()


