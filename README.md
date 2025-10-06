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

### Install prerequisites

Install the following according to your own OS's needs/preferences.

* Makemkv
* git (duh?)
* rsync
* python3.13 or newer + python3.13-venv
* Java? I think makemkv needs that sometimes

### Install `makemkv-headless`

Pick one of the following, either the easy way or the advanced way.  With the
advanced way, you will be running straight from source.  I try to keep `main` as
stable as possible, but it's possible that some bugs slip in.  If that is the
case, you'll need to wait for a fix and update, or manually roll back to a
previous commit.

### The easy way
  
> _Sorry, this way doesn't exist yet.  When it does, it'll be something like
> "install the deb etc then just run it 5head"_

### The "advanced" way

1. `git clone` the repo
2. `./start.sh`
3. Install the dependencies you probably missed
4. Install the dependencies **I** probably missed writing down
5. Repeat #2 again

This will launch a screen session for each of the web and api apps.  The API is
accessible on port `4000` on your local system.  The web interface is accessible
on port `3000`.  Typically at this point you'd open up a browser and go to
http://localhost:3000 or similar.

You can stop the running services by running `./stop.sh` and pairing them
together (stop then start) will restart things if they are already running.

## Usage

### Configuration

## Caveats