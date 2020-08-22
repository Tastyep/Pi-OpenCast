#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# Source profile file as poetry use it to modify the PATH
# This is likely to be done by the display manager, but not always (lightdm).
source ~/.profile

function penv() {
  poetry run "$@"
}

function jenv() {
  PATH="$ROOT/webapp/node_modules:$PATH" eval "$@"
}
