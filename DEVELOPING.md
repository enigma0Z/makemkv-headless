# Development guide

## Requirements

* `uv`
* `node` 23+
* `python` 3.12

## Getting Started

Running these make targets should get your environment up and running to start
development and ensure you can build.

```bash
make all clean-dist run-dev
```

## Architecture

```
├── api -- FastAPI backend API
│   ├── src / makemkv_headless
│   │   ├── api        -- Fastapi request handlers
│   │   ├── config     -- Config object
│   │   ├── disc       -- Disc interface functions
│   │   ├── interface  -- Interface class (semi-deprecated)
│   │   ├── makemkv    -- Functions for talking to makemkv
│   │   ├── mkvtoolnix -- Functions for talking to mkvtoolnix
│   │   ├── models     -- Pydantic data models
│   │   ├── rip_titles -- Higher-order methods for ripping titles
│   │   ├── sort       -- Classes/methods/functions to sort into Jellyfin dirs
│   │   ├── tmdb       -- TMDB client
│   │   └── ui         -- Where the ui dist is stored when built
│   └── test -- Test suites (if I had any)
└── web -- Web UI
    └── src
        ├── api        -- UI API client implementation (Redux)
        │   └── v1
        ├── components -- React components
        ├── pages      -- React pages (router-driven)
        └── util       -- Utility functions (this naming is a crutch)
```

### makemkv_headless.api

The main FastAPI set of request handlers, organized by their direct URI path,
e.g. `api.v1.config` is directly referenced via the URL `/api/v1/config` on the
API server.

### makemkv_headless.config

`Config` class, module and associated bits and parts.  Config is done via a
singleton, `CONFIG`, created by this module on first import.  Typical usage is
like this:

```python
from makemkv_headless.config import CONFIG

CONFIG.whatever_value
CONFIG.whatever_method()
```

You shouldn't need to call the `Config()` constructor, and indeed doing so risks
inconsistent behavior across the app.

#### Config to CLI mapping

The Config model (`makemkv_headless.models.config.ConfigModel`) uses
`json_schema_extra` in the Pydantic fields to add information which is used to
connect a given config option to a given CLI argument automagically.  Note that
calling the config write endpoint will write the options given on the CLI out to
the config file (this behavior is being addressed via #70) 

### makemkv_headless.disc

Methods for interacting with discs, mostly detect disc insertion and enable
eject.

### makemkv_headless.interface

Interface base class + async queue interface.  This is somewhat of a holdover
from a previous design of this application where you could run it on the CLI and
get a curses-based TUI.  That has since been abandoned (though it may be
re-implemented in a separate program interfacing via the API instead of direct
classes like here).

The main thing here is that the way the CLI tools this runs communicate with the
API (and essentially the web UI) is via a `asyncio.queues.Queue` and a queue
read loop which ingests the messages sent to the queue (from various CLI tools)
and then acts upon them.

### makemkv_headless.makemkv

Interface methods for calling `makemkv` from the shell.  All shell interface
methods are given an `interface` object which receives the messages (lines
printed) from the CLI commands and translates them into a format that the web
interface can either display or interpret.

### makemkv_headless.mkvtoolnix

Interface methods for calling `mkvtoolnix` from the shell.

### makemkv_headless.models

Pydantic models for everything, named by their classes.  Not gonna list them
here.

### makemkv_headless.rip_titles

Rip titles function -- Does the heavy lifting for `makemkv_headless.api.v1.rip`
endpoints, calling both the ripping functions from `makemkv` and the sorting
functions from `sort`

### makemkv_headless.sort

Sort classes -- These are structured with inheritance so that the sorter can use
either the TV or Movie sort classes, and the subclasses here ensure everything
goes into the right places.

### makemkv_headless.tmdb

Super bare-bones TMDB client.  Requests out to TMDB and translates responses
into the appropriate pydantic models.

### makemkv_headless.ui

This is basically a placeholder directory where the node `dist` is placed when
you run `make all` -- it's accessed via the python `resources` module and serves
static files via a fastapi handler at `makemkv_headless.api`