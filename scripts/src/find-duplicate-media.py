#!/usr/bin/env python3

import sys

from typing import Callable

from argparse import ArgumentParser
from os import stat
from sys import exit, argv
from pathlib import Path

from heuristics.Match import Match
from heuristics.MatchSet import MatchSet
from heuristics.NamedHeuristic import NamedHeuristic
from heuristics.SizeMatch import CloseSizeMatch, ExactSizeMatch
from heuristics.HeuristicRegistry import get_heuristic

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

parser = ArgumentParser()
parser.add_argument('--globstr', '-g', default="**/*.mkv")
parser.add_argument('paths', nargs='*')
parser.add_argument('--heuristics', nargs='*', default=[ExactSizeMatch.__name__, CloseSizeMatch.__name__])
opts = parser.parse_args(argv[1:])

# Defined heuristics for identifying matches
# heuristics: list[NamedHeuristic] = [ExactSizeMatch, CloseSizeMatch]
heuristics: list[NamedHeuristic] = []

for heuristic in opts.heuristics:
    heuristics.append(get_heuristic(heuristic)())

# Iterate over the paths specified on the CLI
for opts_path in opts.paths:

    # Get the files' paths and stats specified on the CLI
    paths = Path(opts_path).glob(opts.globstr)
    file_db: list[Match] = []
    for path in paths:
        file_db.append(Match(path=path, stat=stat(path)))

    # Store matched files here
    matches: list[MatchSet] = []

    # Iterate through found paths
    for outer_file in file_db:
        for inner_file in [ file for file in file_db if file.path != outer_file.path ]:
            # Check each inner/outer against each heuristic
            for heuristic in heuristics:
                print(heuristic)
                heuristic_matches = heuristic.matcher(outer_file, inner_file)
                print(heuristic_matches)
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