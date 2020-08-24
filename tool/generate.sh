#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/gen_cli.sh"
source "$ROOT/script/env.sh"

#### CLI handlers

function doc() {
  (cd "$ROOT/docs" && penv make clean && penv make html -b coverage)
}

#### Internal functions

declare -A COMMANDS
COMMANDS=(
  [doc]="Generate documentation files."
)
make_basic_cli default_help_display COMMANDS "$@"
