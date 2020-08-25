#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"

#### CLI handlers

function doc() {
  (cd "$ROOT/docs" && penv make clean && penv make html -b coverage)
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [doc]="Generate documentation files."
)
make_cli default_help_display COMMANDS "$@"
