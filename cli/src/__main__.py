#!/usr/bin/env python3

from sys import argv

from cli.parsers import top_level_parser
from cli.subcommands import *

opts = top_level_parser.parse_args(argv[1:])
opts.func(opts)