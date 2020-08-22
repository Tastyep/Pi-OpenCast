#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/gen_cli.sh"

#### CLI handlers

function all() {
  spec
  python
}

function python() {
  flake8 "$ROOT/OpenCast" --statistics && printf "✓ flake8\n"
}

function spec() {
  local cmd output

  exec 5>&1
  cmd="spectral lint "$ROOT/specs/openapi.yml" --verbose --skip-rule info-contact"
  output=$(eval "$cmd" | tee >(cat - >&5))

  if echo "$output" | grep -q "problem"; then
    return 1
  fi

  printf "✓ spectral\n"
}

#### Internal functions

declare -A COMMANDS
COMMANDS=(
  [all]="Run all linters."
  [python]="Run the linter on the python code."
  [spec]="Run the linter on the API spec."
)
make_basic_cli default_help_display COMMANDS "$@"
