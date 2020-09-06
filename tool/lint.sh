#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"
source "$ROOT/script/logging.sh"

#### CLI handlers

all() {
  spec
  python
}

python() {
  penv flake8 "$ROOT/OpenCast" --statistics
  log_status "flake8" "$?"
}

spec() {
  local cmd output status

  jenv "speccy --config $ROOT/specs/.speccy.yml lint $ROOT/specs/openapi.yml"
  log_status "speccy" "$?"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [all]="Run all linters."
  [python]="Run the linter on the python code."
  [spec]="Run the linter on the API spec."
)
make_cli default_help_display COMMANDS "$@"
