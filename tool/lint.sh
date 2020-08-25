#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"
source "$ROOT/script/logging.sh"

#### CLI handlers

function all() {
  spec
  python
}

function python() {
  penv flake8 "$ROOT/OpenCast" --statistics
  log_status "flake8" "$?"
}

function spec() {
  local cmd output status

  exec 5>&1
  cmd="spectral lint "$ROOT/specs/openapi.yml" --verbose --skip-rule info-contact"
  output=$(jenv "$cmd" | tee >(cat - >&5))

  echo "$output" | grep -q "problem" && status=1 || status=0
  log_status "spectral" "$status"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [all]="Run all linters."
  [python]="Run the linter on the python code."
  [spec]="Run the linter on the API spec."
)
make_cli default_help_display COMMANDS "$@"
