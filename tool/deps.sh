#!/usr/bin/env bash
# Usage:
#   ./deps.sh command
#
# Commands:
#   install   Install all dependencies.
#   update    Update python dependencies.

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/env.sh
source "$ROOT/script/env.sh"

install() {
  (cd "$ROOT" && poetry install)
  (cd "$ROOT/webapp" && npm install)
}

update() {
  (cd "$ROOT" && poetry update)
}

parse_args "$@"
${ARGS["command"]}
