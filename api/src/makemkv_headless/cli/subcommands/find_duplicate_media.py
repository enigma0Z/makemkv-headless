from argparse import Namespace
from os import stat
from pathlib import Path
from typing import Callable

from humanfriendly import format_size
from makemkv_headless.cli.parsers import subparsers
from makemkv_headless.heuristics.HeuristicRegistry import (
    get_all_heuristics, get_heuristic)
from makemkv_headless.heuristics.Match import Match
from makemkv_headless.heuristics.MatchSet import MatchSet
from makemkv_headless.heuristics.NamedHeuristic import NamedHeuristic
from makemkv_headless.heuristics.SizeMatch import (CloseSizeMatch,
                                                       ExactSizeMatch)

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

def main(opts: Namespace):
	if opts.list_heuristics:
		print("The following heuristics can be used with the --heuristics argument, e.g. `--heuristics CloseSizeMatch`\n")
		for heuristic in get_all_heuristics():
			print(heuristic, get_heuristic(heuristic).__doc__)
		return

	# Defined heuristics for identifying matches
	# heuristics: list[NamedHeuristic] = [ExactSizeMatch, CloseSizeMatch]
	heuristics: list[NamedHeuristic] = []

	for heuristic in opts.heuristics:
		heuristics.append(get_heuristic(heuristic)())

	print(f'Using heuristics {heuristics}')

	# Iterate over the paths specified on the CLI
	for opts_path in opts.paths:

		# Get the files' paths and stats specified on the CLI
		paths = Path(opts_path).glob(opts.globstr)
		file_db: list[Match] = []
		for path in paths:
			if path.is_file():
				file_db.append(Match(path=path, stat=stat(path)))

		# Store matched files here
		matches: list[MatchSet] = []

		# Iterate through found paths
		for outer_file in file_db:
			for inner_file in [ file for file in file_db if file.path != outer_file.path ]:
				# Check each inner/outer against each heuristic
				for heuristic in heuristics:
					heuristic_matches = heuristic.matcher(outer_file, inner_file, *file_db)
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
			total_storage = 0
			for match in deleted_matches:
				total_storage += match.stat.st_size

			print(f"\nThe following files are marked for deletion ({format_size(total_storage)})")
			print('\n'.join([f'{m.path}' for m in deleted_matches]))
			if input_yes_no("Are you sure you want to delete these files?"):
				for file in deleted_matches:
					if opts.apply:
						print(f'deleting {file.path}')
						Path.unlink(file.path, missing_ok=True)
					else:
						print(f'(dry run) deleting {file.path}')

parser = subparsers.add_parser('find-duplicate-media', help='Apply heuristics to a media directory to identify potentially duplicate files (either true duplicates, or extra versions of the same media)')
parser.set_defaults(func=main)
parser.add_argument('--globstr', '-g', default="**/*.mkv", help='The glob to use to find files')
parser.add_argument('--apply', help='Actually delete files', action='store_true')
parser.add_argument('paths', nargs='*', help='The path to look for files in')
parser.add_argument('--heuristics', nargs='*', default=[ExactSizeMatch.__name__, CloseSizeMatch.__name__], help="Which heuristics to use to match files together")
parser.add_argument('--list-heuristics', action="store_true", help="List all available heuristics")
