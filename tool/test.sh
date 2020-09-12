#!/usr/bin/env bash
# Usage:
#   ./test.sh command [<selector>] [--coverage]
#
# Commands:
#   all    Run all tests.
#   back   Run the test suite of the python application.
#   front  Run the test suite of the web application.
#
# Options:
#   --coverage  Mesure test coverage.

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
  back "$@" && front "$@"
}

back() {
  local command selector
  command=("python")
  selector="discover"
  [[ "${ARGS["--coverage"]}" == true ]] && command=("coverage" "run")
  [[ -n "${ARGS["selector"]}" ]] && selector="${ARGS["selector"]}"

  penv "${command[@]}" -m unittest "$selector" -v
  local status="$?"

  [[ "${ARGS["--coverage"]}" == true ]] && penv coverage xml
  log_status "Python" "$status"
}

front() {
  printf "Webapp: no test available\n"
  log_status "Webapp" "0"
}

parse_args "$@"
${ARGS["command"]}
