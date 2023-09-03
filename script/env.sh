#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

penv() {
  if [[ "$(pwd)" == "$ROOT"* ]]; then
    poetry run "$@"
  else
    (cd "$ROOT" && poetry run "$@")
  fi
}

jenv() {
  local node_modules_path

  node_modules_path="$ROOT/webapp/node_modules/.bin"
  if [[ "$PATH" != *"$node_modules_path"* ]]; then
    export PATH="$PATH:$node_modules_path"
    (cd "$ROOT/webapp/" && npm install --only=dev)
  fi
  "$@"
}
