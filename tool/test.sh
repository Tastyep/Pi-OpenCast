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
  local -a params
  local -A parsed
  params=("--coverage" "[<selector>]")
  expect_params params parsed "back" "$@"

  local command selector
  command="python"
  selector="discover"
  [[ ! -z "${parsed["--coverage"]}" ]] && command="coverage run"
  [[ ! -z "${parsed["selector"]}" ]] && selector="${parsed["selector"]}"

  penv "$command -m unittest $selector -v"
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
