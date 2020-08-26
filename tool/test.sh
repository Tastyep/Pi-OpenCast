#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"
source "$ROOT/script/logging.sh"

#### CLI handlers

function all() {
  back
  front
}

function back() {
  if [[ -z "$1" ]]; then
    penv python -m unittest discover -v
  else
    local selector="$1"

    if [[ "$selector" != "$TEST_DIR"* ]]; then
      selector="$TEST_DIR.$selector"
    fi
    penv python -m unittest "$selector"
  fi
  log_status "Python" "$?"
}

function front() {
  printf "Webapp: no test available\n"
  log_status "Webapp" "0"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [all]="Run all tests."
  [back]="Run the test suite of the python application."
  [front]="Run the test suite of the web application."
)
make_cli default_help_display COMMANDS "$@"
