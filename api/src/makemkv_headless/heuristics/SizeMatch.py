
from os import path

from .HeuristicRegistry import register_heuristic

from .NamedHeuristic import NamedHeuristic
from .Match import Match


class SizeMatch(NamedHeuristic):
    def match_info(self, m: Match):
        return f'Size is {m.stat.st_size} bytes'

class CloseSizeMatch(SizeMatch):
    '''
    Match files which are close in size (default of within 1%) -- This is
    designed to catch multiple language versions of the same media, where the
    title itself is essentially the same, but different title / credit
    sequences, scenes, or audio are added for the other language(s)
    '''
    _THRESHOLD = 0.01 # 1%

    @staticmethod
    def name():
        return f"Close Size Match (within {CloseSizeMatch._THRESHOLD})"

    def matcher(self, a: Match, b: Match, *matches: list[Match]) -> bool:
        if (
            a.stat.st_size > 1024*4 and
            abs(a.stat.st_size - b.stat.st_size) / a.stat.st_size < CloseSizeMatch._THRESHOLD
        ):
            return [a, b]

register_heuristic(CloseSizeMatch)

class ExactSizeMatch(SizeMatch):
    '''
    Match files which are the _exact same size_.  Primarily this is meant to
    catch duplicate media, but a stronger heuristic (such as md5/sha sums) could
    also be used here in the future.
    '''
    @staticmethod
    def name():
        return f"Exact Size Match"

    def matcher(self, a: Match, b: Match, *matches: list[Match]) -> bool:
        if a.stat.st_size == b.stat.st_size:
            return [a, b]

register_heuristic(ExactSizeMatch)

class DiskSizeMatch(SizeMatch):
    '''
    Match files which are the sum total (within 5%) of all other media in the
    same folder.  This is meant to catch media which includes a playlist of the
    entire disc as another item.
    '''
    _THRESHOLD = 0.05 # 5%

    @staticmethod
    def name():
        return "Disk size match"
    
    def matcher(self, a: Match, _: Match, *matches: Match):
        total_size = 0
        for match in [ match for match in matches if match.path != a.path ]:
            total_size += match.stat.st_size

        if abs(total_size - a.stat.st_size) / a.stat.st_size < self._THRESHOLD:
            return [a]

register_heuristic(DiskSizeMatch)

def is_show(a: Match) -> bool:
    return '/shows/' in str(a.path)

def is_extras(a: Match) -> bool:
    return path.split(a.path)[0].endswith('extras')

class EpisodeMultipleMatch(NamedHeuristic):
    '''
    Match episodic content (shows) where an extra is larger than the episode
    size by a significant factor (default 1.9x, essentially aiming at the length
    of two episodes or more, excluding title sequences).
    '''
    _FACTOR = 1.9 # Anything which is essentially 2x the average episode size

    @staticmethod
    def name():
        return "Episode Multiple Match"
    
    def matcher(self, a: Match, b: Match, *matches: Match) -> list[Match]:
        if (
            is_show(a) and is_extras(a)
        ):
            total_episode_sizes = 0
            episodes = [ 
                match 
                for match in matches 
                if not is_extras(match)
            ]

            for episode in episodes:
                total_episode_sizes += episode.stat.st_size

            average_episode_size = total_episode_sizes / len(episodes)
            target_match_size = average_episode_size * EpisodeMultipleMatch._FACTOR

            print(a.path, b.path, average_episode_size, target_match_size, a.stat.st_size)

            if a.stat.st_size > target_match_size:
                return [a]

register_heuristic(EpisodeMultipleMatch)