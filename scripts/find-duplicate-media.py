#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Callable, Type

from pydantic import BaseModel, ConfigDict

from argparse import ArgumentParser
from os import stat, sep, stat_result
from sys import exit, argv
from pathlib import Path
class Match(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    path: Path
    stat: stat_result

# Heuristics
class NamedHeuristic:
    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def matcher(a: Match, b: Match, *matches: list[Match]) -> list[Match]:
        pass

    @staticmethod
    @abstractmethod
    def match_info(m: Match) -> str:
        pass

class SizeMatch(NamedHeuristic):
    @staticmethod
    def match_info(m: Match):
        return f'Size is {m.stat.st_size} bytes'

class CloseSizeMatch(SizeMatch):
    _THRESHOLD = 0.01 # 1%

    @staticmethod
    def name():
        return f"Close Size Match (within {CloseSizeMatch._THRESHOLD})"

    @staticmethod
    def matcher(a: Match, b: Match, *matches: list[Match]) -> bool:
        if (
            a.stat.st_size > 1024*4 and
            abs(a.stat.st_size - b.stat.st_size) / a.stat.st_size < CloseSizeMatch._THRESHOLD
        ):
            return [a, b]

class ExactSizeMatch(SizeMatch):
    @staticmethod
    def name():
        return f"Exact Size Match"

    @staticmethod
    def matcher(a: Match, b: Match, *matches: list[Match]) -> bool:
        if a.stat.st_size == b.stat.st_size:
            return [a, b]

def input_loop(prompt: str, validator: Callable[[any], bool]):
    while True:
        res = input(f'{prompt}\n> ')
        if (validator(res)):
            break
    return res

def input_yes_no(prompt: str) -> bool:
    return input_loop(
        f'{prompt} [Y]es / [N]o',
        lambda x: x.casefold() in ['y', 'yes', 'n', 'no']
    ).casefold().startswith('y')

class MatchSet(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    heuristic: Type[NamedHeuristic]
    match_key: Path
    matches: list[Match] = []

parser = ArgumentParser()
parser.add_argument('--globstr', '-g', default="**/*.mkv")
parser.add_argument('paths', nargs='*')
opts = parser.parse_args(argv[1:])

# Iterate over the paths specified on the CLI
for opts_path in opts.paths:

    # Get the files' paths and stats specified on the CLI
    paths = Path(opts_path).glob(opts.globstr)
    file_db: list[Match] = []
    for path in paths:
        file_db.append(Match(path=path, stat=stat(path)))

    # Defined heuristics for identifying matches
    # heuristics: list[NamedHeuristic] = [ExactSizeMatch, CloseSizeMatch]
    heuristics: list[NamedHeuristic] = [CloseSizeMatch]

    # Store matched files here
    matches: list[MatchSet] = []

    # Iterate through found paths
    for outer_file in file_db:
        for inner_file in [ file for file in file_db if file.path != outer_file.path ]:
            # Check each inner/outer against each heuristic
            for heuristic in heuristics:
                heuristic_matches = heuristic.matcher(outer_file, inner_file)
                if heuristic_matches:
                    
                    # This should be a list of either 1 or 0.  If it's more than one, something bad happened
                    match_sets = [m for m in matches if m.heuristic == heuristic and (outer_file in m.matches or inner_file in m.matches)]
                    if len(match_sets) == 1:
                        for match_item in heuristic_matches:
                            if match_item not in match_sets[0].matches:
                                match_sets[0].matches.append(match_item)

                    elif len(match_sets) > 1:
                        raise Exception('Error in match sets, duplicate entry found')

                    else:
                        match_set = MatchSet(heuristic=heuristic, match_key=outer_file.path, matches=heuristic_matches)
                        matches.append(match_set)

    # Record which matches were already acted upon so we can ignore them if they matched more than one heuristic
    deleted_matches: list[Match] = [] 
    for match in matches:
        print(f'A {match.heuristic.name()} was found for the following files')
        for index, match_item in enumerate(match.matches):
            # Print matches
            print(f'{index} {match_item.path} - {match.heuristic.match_info(match_item)}{' (already marked for deletion)' if match_item in deleted_matches else ''}')
            # Provide TUI to do something about them
            # Record acted-upon matches (essentially, deleted ones) in deleted_matches
        print()
        for match_item in [match for match in match.matches if match not in deleted_matches]:
            print(match_item.path)
            if input_yes_no("Do you want to delete this file?"):
                print(f'Marking {match_item.path} for deletion')
                deleted_matches.append(match_item)

            print()

    if deleted_matches:
        print("\nThe following files are marked for deletion")
        print('\n'.join([f'{m.path}' for m in deleted_matches]))
        if input_yes_no("Are you sure you want to delete these files?"):
            for file in deleted_matches:
                print(f'deleting {file.path}')
                Path.unlink(file.path, missing_ok=True)