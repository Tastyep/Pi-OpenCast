#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/gen_cli.sh"
source "$ROOT/script/env.sh"

#### CLI handlers

function all() {
  spec
  python
}

function python() {
  penv flake8 "$ROOT/OpenCast" --statistics
  display_linter_status "flake8" "$?"
}

function spec() {
  local cmd output status

  exec 5>&1
  cmd="spectral lint "$ROOT/specs/openapi.yml" --verbose --skip-rule info-contact"
  output=$(jenv "$cmd" | tee >(cat - >&5))

  echo "$output" | grep -q "problem" && status=1 || status=0
  display_linter_status "spectral" "$status"
}

#### Internal functions

function display_linter_status() {
  local name status marker

  name="$1"
  status="$2"
  [[ "$status" == "1" ]] && marker="✗" || marker="✓"

  printf "$marker $name\n"
  return "$status"
}

declare -A COMMANDS
COMMANDS=(
  [all]="Run all linters."
  [python]="Run the linter on the python code."
  [spec]="Run the linter on the API spec."
)
make_basic_cli default_help_display COMMANDS "$@"
