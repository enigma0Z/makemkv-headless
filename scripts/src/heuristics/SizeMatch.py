
from .HeuristicRegistry import register_heuristic

from .NamedHeuristic import NamedHeuristic
from .Match import Match


class SizeMatch(NamedHeuristic):
    def match_info(self, m: Match):
        return f'Size is {m.stat.st_size} bytes'

class CloseSizeMatch(SizeMatch):
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
    @staticmethod
    def name():
        return f"Exact Size Match"

    def matcher(self, a: Match, b: Match, *matches: list[Match]) -> bool:
        if a.stat.st_size == b.stat.st_size:
            return [a, b]

register_heuristic(ExactSizeMatch)