from argparse import ArgumentParser

from sys import exit

def default(*args):
	top_level_parser.print_help()
	exit(1)

top_level_parser = ArgumentParser(prog='mmh')
top_level_parser.set_defaults(func=default)
subparsers = top_level_parser.add_subparsers()