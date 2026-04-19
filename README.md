# Makemkv Headless

A headless interface for [makemkv](https://makemkv.com).

## Overview and features

* Designed to integrate tightly with [Jellyfin](https://jellyfin.org)'s
	organization schema for files
* Built-in [TMDB](https://www.themoviedb.org) lookup for media titles, name
	(formatting), etc. to make it easier for Jellyfin to find your media
* Mobile or desktop friendly interface
* Frontend web interface built in Typescript using [React](https://react.dev)
	with [Vite](https://vite.dev/guide/)
* Backend built in Python with [FastApi](https://fastapi.tiangolo.com)

## Installation

### Prerequisites

* [Python 3.12](https://www.python.org/downloads/)
* [makemkv](https://makemkv.com/download/)
* [pipx](https://pipx.pypa.io/stable/how-to/install-pipx/) (not required but
  very useful)

### Installing makemkv-headless

```bash
pipx install makemkv-headless
```

## Running

```bash
mmh --help
```

You can now access the UI from a web browser at http://127.0.0.1:4000.  Running
on a remote system may potentially require setting cors origins depending on
your setup, but for most basic setups it probably isn't required.