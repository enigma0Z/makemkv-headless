# MakeMKV Headless CLI

A CLI for a server for MakeMKV

## Usage

```bash
mmh <subcommand> <subcommand args>
```

## Subcommands

### Find Duplicate Media

```
usage: mmh find-duplicate-media [-h] [--globstr GLOBSTR] [--apply] [--heuristics [HEURISTICS ...]] [--list-heuristics] [paths ...]

positional arguments:
  paths                 The path to look for files in

options:
  -h, --help            show this help message and exit
  --globstr, -g GLOBSTR
                        The glob to use to find files
  --apply               Actually delete files
  --heuristics [HEURISTICS ...]
                        Which heuristics to use to match files together
  --list-heuristics     List all available heuristics
```