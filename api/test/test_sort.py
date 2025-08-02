import json
from unittest import TestCase
from unittest.mock import DEFAULT, MagicMock, patch

from src.sort import ShowInfo, SortInfo, sort_titles
from src.toc import TOC

from .data.toc_test_data import generate_CINFO, generate_SINFO, generate_TINFO

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

@patch.multiple(
  'sort',
  remove=DEFAULT, rename=DEFAULT, # os
  rmtree=DEFAULT, # shutil
  logging=DEFAULT,
  split_mkv=DEFAULT, # mkvtoolnix
  rsync=DEFAULT
)
class SortTest(TestCase):
  def test_SortInfo(self, **mock):
    test_sort_info = SortInfo(
      name='movie name',
      id='movie_id',
      main_indexes=[0],
      extra_indexes=[1,2,3]
    )

    self.assertEqual('movie_name [tmdbid-movie_id]', test_sort_info.base_path())
    self.assertEqual('movie_name [tmdbid-movie_id] - 0.mkv', test_sort_info.next_file())
    self.assertEqual('movie_name [tmdbid-movie_id] - 1.mkv', test_sort_info.next_file())

    # SortInfo serializes to JSON
    self.assertEqual(json.dumps({
      "name": "movie name", 
      "id": "movie_id", 
      "main_indexes": [0], 
      "extra_indexes": [1, 2, 3], 
      "split_segments": [], 
      "id_db": "tmdbid", 
      "index": 1
    }), test_sort_info.to_json())

  def test_ShowInfo(self, **mock):
    test_sort_info = ShowInfo(
      name='show name',
      id='show_id',
      main_indexes=[0],
      extra_indexes=[1,2,3],
      season_number=1,
      first_episode=1
    )

    self.assertEqual('show_name [tmdbid-show_id]', test_sort_info.base_path())
    self.assertEqual('show_name [tmdbid-show_id]/Season 01', test_sort_info.path())
    self.assertEqual('show_name S01E01.mkv', test_sort_info.next_file())
    self.assertEqual('show_name S01E02.mkv', test_sort_info.next_file())

  def test_sort_show(self, **mock):
    sort_info = ShowInfo(
      name='show_name',
      id='show_id',
      main_indexes=[0,1],
      extra_indexes=[2],
      season_number=1,
      first_episode=1
    )

    sort_titles(
      mock_toc,
      'rip_path_base',
      'user@host:dest_path_base',
      sort_info=sort_info,
      interface=mock_interface
    )

    # Shows are organized by show name, season, and episode
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/filename.mkv', 
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/show_name S01E01.mkv'
      ), 
      mock['rename'].call_args_list[0].args
    )
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/filename.mkv', 
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/show_name S01E02.mkv'
      ), 
      mock['rename'].call_args_list[1].args
    )
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/filename.mkv', 
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/extras/name1___filename.mkv'
      ), 
      mock['rename'].call_args_list[2].args
    )

    # RSync copies from source to dest dir
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]', 
        'user@host:dest_path_base'
      ),
      mock['rsync'].call_args[0]
    )

  def test_sort_show_split_chapters(self, **mock):
    sort_info = ShowInfo(
      name='show_name',
      id='show_id',
      main_indexes=[0],
      extra_indexes=[2],
      season_number=1,
      first_episode=1,
      split_segments=[1,3,5]
    )

    sort_titles(
      mock_toc,
      'rip_path_base',
      'user@host:dest_path_base',
      sort_info=sort_info,
      interface=mock_interface
    )

    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/filename.mkv',
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/split-%d.mkv', 
        [1, 3, 5]
      ),
      mock['split_mkv'].call_args[0]
    )

    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/split-1.mkv', 
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/show_name S01E01.mkv'
      ),
      mock['rename'].call_args_list[0].args
    )
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/split-2.mkv', 
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/show_name S01E02.mkv'
      ),
      mock['rename'].call_args_list[1].args
    )
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/split-3.mkv', 
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/show_name S01E03.mkv'
      ),
      mock['rename'].call_args_list[2].args
    )
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/split-4.mkv', 
        'rip_path_base/show_name [tmdbid-show_id]/Season 01/show_name S01E04.mkv'
      ),
      mock['rename'].call_args_list[3].args
    )

  def test_sort_movie(self, **mock):
    sort_info = SortInfo(
      name='show_name',
      id='movie_id',
      main_indexes=[0,1],
      extra_indexes=[2]
    )

    sort_titles(
      mock_toc,
      'rip_path_base',
      'user@host:dest_path_base',
      sort_info=sort_info,
      interface=mock_interface
    )

    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-movie_id]/filename.mkv', 
        'rip_path_base/show_name [tmdbid-movie_id]/show_name [tmdbid-movie_id] - 0.mkv'
      ),
      mock['rename'].call_args_list[0].args
    )
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-movie_id]/filename.mkv', 
        'rip_path_base/show_name [tmdbid-movie_id]/show_name [tmdbid-movie_id] - 1.mkv'
      ),
      mock['rename'].call_args_list[1].args
    )
    self.assertEqual(
      (
        'rip_path_base/show_name [tmdbid-movie_id]/filename.mkv', 
        'rip_path_base/show_name [tmdbid-movie_id]/extras/name1___filename.mkv'
      ),
      mock['rename'].call_args_list[2].args
    )