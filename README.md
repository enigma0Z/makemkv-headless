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

* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* [node](https://nodejs.org/en/download)
* [makemkv](https://makemkv.com/download/)

### Building everything

```bash
make clean && make
```

### API only

```bash
cd api && uv sync
```

### CLI (deprecated)

```bash
cd cli && uv sync
```

### WEB

```bash
cd web && npm install
```

## Setup

1. Copy `config.example.yaml` to `config.yaml`
2. Get your own [TMDB API key](https://developer.themoviedb.org/docs/getting-started) and put it in here 

## Running everything

### From source / development mode

```bash
make
./start.sh --ui-path web/dist # api options; use --help to see what there is
```

### In production-ish

This part is not yet done, but we can do it from built source

```bash
make
./start.sh screen <listen port> # api options ...
```

If you give `start.sh` `screen` and a port it will run in a screen session and
give you back your terminal.