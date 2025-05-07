from os import path, remove, rename, makedirs
from shutil import rmtree

import logging
logger = logging.getLogger(__name__)

import features

from interface import Interface, Target
from mkvtoolnix import split_mkv
from toc import TOC
from util import rsync, sanitize

class SortInfo:
  def __init__(
      self,
      name: str,
      id: str,
      main_indexes: list[int],
      extra_indexes: list[int],
      split_segments: list[int] = [],
      id_db: str = 'tmdbid',
      **kwargs
  ):
    self.name = name
    self.id = id
    self.main_indexes = main_indexes
    self.extra_indexes = extra_indexes
    self.split_segments = split_segments
    self.id_db = id_db
    self.index = -1 # The first call of next_file will increment to 0

  def path(self):
    return self.base_path()

  def base_path(self):
    return f'{sanitize(self.name)} [{self.id_db}-{self.id}]'

  def file(self):
    return f'{self.path()} - {self.index}.mkv'

  def next_file(self):
    self.index += 1
    return self.file()

  def __str__(self):
    return self.path()

class ShowInfo(SortInfo):
  def __init__(
      self,
      season_number: int,
      first_episode: int,
      **kwargs
  ):
    self.season_number = season_number
    self.first_episode = first_episode
    super().__init__(**kwargs)

  def path(self):
    return path.join(super().path(), f'Season {self.season_number:02d}')

  def file(self):
    return f'{sanitize(self.name)} S{self.season_number:02d}E{self.first_episode + self.index:02d}.mkv'

  def __str__(self):
    return f'{self.path()} - First Episode: {self.first_episode}'

def sort_titles(
    toc: TOC,
    rip_path_base: str,  # /tmp/XXXXXX
    dest_path_base: str, # user@host:/path/to/media/library
    sort_info: SortInfo,
    interface: Interface,
):
  failed_titles = []
  rip_path = path.join(rip_path_base, sort_info.path())

  try:
    if features.DO_SORT:
      # episode_indexes refers to the title number on the disk.  This may be
      # title 02, 03, 04, 05, 08, etc... for a set of sequential episodes.
      # Enumerating here transforms this unordered non-sequential list into a
      # sequential list of integers, which is why we discard title here in
      # favor of _index_
      for index in sort_info.main_indexes:
        title = toc.source.titles[int(index)]
        if features.DO_SPLIT and sort_info.split_segments:
          logger.info('Splitting segments', sort_info.split_segments)
          split_mkv(
            path.join(rip_path, title.filename), 
            path.join(rip_path, 'split-%d.mkv'),
            sort_info.split_segments,
            interface=interface
          )
          for segment_index in range(0, len(sort_info.split_segments)+1):
            try:
              sort_file = sort_info.next_file()
              interface.print(f'Sorting Title {sort_file}', target=Target.SORT)
              rename(
                path.join(rip_path, f'split-{segment_index+1}.mkv'),
                path.join(rip_path, sort_file)
              )
            except FileNotFoundError as ex:
              interface.print('Failed to rename segment', segment_index, target=Target.SORT)
              interface.print(ex, target=Target.SORT)
              failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}, Segment {segment_index}\n{ex}')
          if (features.DO_CLEANUP):
            remove(path.join(rip_path, title.filename))
        else:
          try:
            sort_file = sort_info.next_file()
            interface.print(f'Sorting Title {sort_file}', target=Target.SORT)
            rename(
              path.join(rip_path, title.filename), 
              path.join(rip_path, sort_file)
            )
          except FileNotFoundError as ex:
            failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}\n{ex}')

      for index in sort_info.extra_indexes:
        title = toc.source.titles[int(index)]
        try:
          interface.print(f'Sorting Extra {toc.source.name} - {title.filename}', target=Target.SORT)
          rename(
            path.join(rip_path, title.filename), 
            path.join(rip_path, 'extras', f'{sanitize(toc.source.name)}___{title.filename}')
          )
        except FileNotFoundError as ex:
          failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}\n{ex}')

      if len(failed_titles) > 0:
        logger.error(f"Some titles failed to rip or copy, {failed_titles}")
        interface.print("Some titles failed to rip or copy", target=Target.SORT)
        for title in failed_titles:
          interface.print(title, target=Target.SORT)

    if features.DO_COPY:
      rsync(
        path.join(rip_path_base, sort_info.base_path()), 
        path.join(dest_path_base, sort_info.base_path()), 
        interface=interface
      )

  finally:
    if features.DO_CLEANUP:
      interface.print(f"Cleaning up {rip_path_base}", target=Target.SORT)
      logger.info(f"Cleaning up {rip_path_base}")
      rmtree(rip_path_base)
    else:
      interface.print(f"Leaving rip source at {rip_path_base}", target=Target.SORT)