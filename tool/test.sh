#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/env.sh
source "$ROOT/script/env.sh"
# shellcheck source=script/logging.sh
source "$ROOT/script/logging.sh"

#### CLI handlers

all() {
  back "$@"
  front "$@"
}

back() {
  # shellcheck disable=SC2034
  local -a params=("--coverage" "[<selector>]")
  local -A parsed
  expect_params params parsed "back" "$@"

  local command selector
  command=("python")
  selector="discover"
  [[ -n "${parsed["--coverage"]}" ]] && command=("coverage" "run")
  [[ -n "${parsed["selector"]}" ]] && selector="${parsed["selector"]}"

  penv "${command[@]}" -m unittest "$selector" -v
  log_status "Python" "$?"

  [[ -n "${parsed["--coverage"]}" ]] && penv coverage xml
}

front() {
  printf "Webapp: no test available\n"
  log_status "Webapp" "0"
}

#### CLI definition

declare -A COMMANDS
export COMMANDS=(
  [all]="Run all tests."
  [back]="Run the test suite of the python application."
  [front]="Run the test suite of the web application."
)
make_cli default_help_display COMMANDS "$@"
