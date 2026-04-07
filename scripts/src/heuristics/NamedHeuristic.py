from abc import abstractmethod

from .Match import Match


class NamedHeuristic:
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def matcher(self, a: Match, b: Match, *matches: list[Match]) -> list[Match]:
        pass

    @abstractmethod
    def match_info(self, m: Match) -> str:
        pass
