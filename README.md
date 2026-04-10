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

### API

```bash
cd api && uv sync
```

### CLI

```bash
cd cli && uv sync
```

### WEB

```bash
cd web && npm install
```

## Setup

1. Copy `api/config.example.yaml` to `api/config.yaml`
2. Get your own [TMDB API key](https://developer.themoviedb.org/docs/getting-started) and put it in here 

## Running everything

### From source / development mode

```bash
./start.sh <api port> <web port> <api options...>
```

### In production

This part is not yet done.  The goal, however, is something like this from the
CLI package.

```bash
# Run a package install command... then
mmh start <api port> <web port> <api options...>
```