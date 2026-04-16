#!/usr/bin/env bash

BUMP="$1"

if [[ "$BUMP" != "major" ]] && [[ "$BUMP" != "minor" ]] && [[ "$BUMP" != "patch" ]]; then
  echo "No version bump selected"
  exit 1
fi

UV_OPTS="--project api"

release_version=$(git tag | egrep "\d+\.\d+\.\d+" | sort --version-sort | tail -n1)
release_major=$(cut -d. -f1 <<< "$release_version")
release_minor=$(cut -d. -f2 <<< "$release_version")
release_patch=$(cut -d. -f3 <<< "$release_version")

current_version=$(uv --project api version --short)
current_major=$(cut -d. -f1 <<< "$current_version")
current_minor=$(cut -d. -f2 <<< "$current_version")
current_patch=$(cut -d. -f3 <<< "$current_version")
current_dev=$(cut -d. -f4 <<< "$current_version")

echo release: $release_version $release_major $release_minor $release_patch
echo current: $current_version $current_major $current_minor $current_patch

do_bump=0
if [[ $current_major -eq $release_major ]]; then
  if [[ "$BUMP" == "major" ]]; then
    do_bump=1
  elif [[ $current_minor -eq $release_minor ]]; then
    if [[ "$BUMP" == "minor" ]]; then
      do_bump=1
    elif [[ $current_patch -eq $release_patch ]]; then
      if [[ "$BUMP" == "patch" ]]; then
        do_bump=1
      fi
    fi
  fi
fi

BUMP_OPTS=""

if [[ $do_bump -eq 1 ]]; then
  BUMP_OPTS="$BUMP_OPTS --bump $BUMP"
fi

BUMP_OPTS="$BUMP_OPTS --bump dev" 

uv $UV_OPTS version $BUMP_OPTS