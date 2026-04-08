from sys import argv

from .parsers import top_level_parser

# Subcommands self-register themselves with the argument parser, ignore the
# "unused imports" warning
from .subcommands import find_duplicate_media 

def main():
	opts = top_level_parser.parse_args(argv[1:])
	opts.func(opts)