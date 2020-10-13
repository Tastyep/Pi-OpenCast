#!/usr/bin/env bash
# Usage:
#   ./generate.sh command
#
# Commands:
#   doc   Generate documentation files.

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/env.sh
source "$ROOT/script/env.sh"

#### CLI handlers

doc() {
  (cd "$ROOT/docs" && penv make clean && penv make html -b coverage)
}

parse_args "$@"
${ARGS["command"]}
