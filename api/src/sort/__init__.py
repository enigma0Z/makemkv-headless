import logging
logger = logging.getLogger(__name__)

from os import path, remove, rename, makedirs
from shutil import rmtree

from random import sample
from string import ascii_lowercase

from pydantic import PrivateAttr

from src.interface.base_interface import BaseInterface
from src.interface.target import Target
from src.models.sort import ShowInfoModel, SortInfoModel


from src import features
from src.interface import get_interface
from src.json_serializable import JSONSerializable
from src.mkvtoolnix import split_mkv
from src.toc import Toc
from src.util import rsync, sanitize

class SortInfo(SortInfoModel):
  # Initialize to -1 to prevent oboe with next_file()
  _index: int = PrivateAttr(default=-1) 

  def path(self):
    return self.base_path()

  def base_path(self):
    return f'{sanitize(self.name)} [{self.id_db}-{self.id}]'

  def file(self):
    return f'{self.path()} - {self._index}.mkv'

  def next_file(self):
    self._index += 1
    return self.file()

  def __str__(self):
    return self.path()

class ShowInfo(ShowInfoModel, SortInfo):
  def path(self):
    return path.join(super().path(), f'Season {self.season_number:02d}')

  def file(self):
    return f'{sanitize(self.name)} S{self.season_number:02d}E{self.first_episode + self._index:02d}.mkv'

  def __str__(self):
    return f'{self.path()} - First Episode: {self.first_episode}'

async def sort_titles(
    toc: Toc,
    rip_path_base: str,  # /tmp/XXXXXX
    dest_path_base: str, # user@host:/path/to/media/library
    sort_info: SortInfo,
    interface: BaseInterface = get_interface(),
):

  unique_identifier = ''.join(sample(ascii_lowercase, 8))

  logger.debug(
    'sort_titles() called with args; ' 
    f'toc: {toc}, ' 
    f'rip_path_base: {rip_path_base}, ' 
    f'dest_path_base: {dest_path_base}, '
    f'sort_info: {sort_info}, ' 
    f'interface: {interface}'
  )
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
              failed_titles.append(f'{index}: {title.filename}, {title.runtime}, Segment {segment_index}\n{ex}')
          if (features.DO_CLEANUP):
            remove(path.join(rip_path, title.filename))
        else:
          try:
            sort_file = sort_info.next_file()
            interface.print(f'Sorting Title {sort_file}', target=Target.SORT)
            logger.info(f'Sorting Title {path.join(rip_path, title.filename)} to {path.join(rip_path, sort_file)}')
            rename(
              path.join(rip_path, title.filename), 
              path.join(rip_path, sort_file)
            )
          except FileNotFoundError as ex:
            failed_titles.append(f'{index}: {title.filename}, {title.runtime}\n{ex}')

      for index in sort_info.extra_indexes:
        try:
          title = toc.source.titles[int(index)]
          interface.print(f'Sorting Extra {toc.source.name} - {title.filename}', target=Target.SORT)
          rename(
            path.join(rip_path, title.filename), 
            path.join(rip_path, 'extras', f'{sanitize(toc.source.name)}___{unique_identifier}___{title.filename}')
          )
        except IndexError as ex:
          failed_titles.append(f'{index}: {title.filename}, {title.runtime}\n{ex}')
          logger.error(f"Could not locate title with index {index} to sort as an extra. extra_indexes: {sort_info.extra_indexes}, len(toc.source.titles): {len(toc.source.titles)}\n{ex}")
        except FileNotFoundError as ex:
          failed_titles.append(f'{index}: {title.filename}, {title.runtime}\n{ex}')
          logger.error(f"Could not locate title with filename {title.filename} to sort as an extra\n{ex}")

      if len(failed_titles) > 0:
        logger.error(f"Some titles failed to rip or copy, {failed_titles}")
        interface.print("Some titles failed to rip or copy", target=Target.SORT)
        for title in failed_titles:
          interface.print(title, target=Target.SORT)

    if features.DO_COPY:
      await rsync(
        path.join(rip_path_base, sort_info.base_path()), 
        dest_path_base, 
        interface=interface
      )

  finally:
    if features.DO_CLEANUP:
      interface.print(f"Cleaning up {rip_path_base}", target=Target.SORT)
      logger.info(f"Cleaning up {rip_path_base}")
      rmtree(rip_path_base)
    else:
      interface.print(f"Leaving rip source at {rip_path_base}", target=Target.SORT)