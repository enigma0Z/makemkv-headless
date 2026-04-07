#!/usr/bin/env python3

from pydantic import BaseModel

from argparse import ArgumentParser
from os import stat, sep, stat_result
from sys import exit, argv
from pathlib import Path

class Match(BaseModel):
    path: Path
    stat: stat_result

class MatchSet(BaseModel):
    key: Path
    matches: list[Match] = []

type Heuristic = callable[[Match, Match], bool]

class NamedHeuristic(BaseModel):
    name: str
    matcher: callable[[Match, Match], bool]

class CloseSizeMatch(NamedHeuristic):
    THRESHOLD = 0.01 # 1%
    name = "Close Size Match"
    @staticmethod
    def matcher(a: Match, b: Match) -> bool:
        return abs(a.stat.st_size / b.stat.st_size) < CloseSizeMatch.THRESHOLD

class ExactSizeMatch(NamedHeuristic):
    name = "Exact Size Match"
    @staticmethod
    def matcher(a: Match, b: Match) -> bool:
        return a.stat.st_size == b.stat.st_size

parser = ArgumentParser()
parser.add_argument('--apply', '-a', action='store_true')
parser.add_argument('paths', nargs='*')
opts = parser.parse_args(argv[1:])

for opts_path in opts.paths:
    paths = Path(opts_path).glob('**/*.mkv')
    file_db: list[Match] = []

    for path in paths:
        file_db.append(Match(path=path, stat=stat(path)))

    heuristics: list[NamedHeuristic] = [ExactSizeMatch, CloseSizeMatch]
    matches: dict[str, dict[str, list[Match]]] = {h.__name__: {} for h in heuristics}

    for heuristic in heuristics:
        matches[heuristic.__name__] = []

    for outer_file in file_db:
        for inner_file in [ file for file in file_db if file.path != outer_file.path ]:
            for heuristic in heuristics:
                if heuristic.matcher(outer_file, inner_file):
                    if outer_file not in matches[heuristic.__name__]:
                        matches[heuristic.__name__][outer_file.path] = [outer_file]

                    matches[heuristic.__name__][outer_file.path] = [inner_file]

    for heuristic, match_set in matches:
        print(heuristic)
        for _, match_list in match_set:
            print(match_list)