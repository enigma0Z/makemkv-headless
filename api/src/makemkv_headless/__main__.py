from sys import argv

from makemkv_headless.cli import top_level_parser

def main():
	opts = top_level_parser.parse_args(argv[1:])
	opts.func(opts)

if __name__ == '__main__':
	main()