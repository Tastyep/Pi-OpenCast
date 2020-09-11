#!/usr/bin/env bash
# Usage:
#   ./serve.sh command
#
# Commands:
#   spec  View specifications in beautiful human readable documentation.

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/env.sh
source "$ROOT/script/env.sh"

#### CLI handlers

spec() {
  jenv "speccy --config $ROOT/specs/.speccy.yml serve $ROOT/specs/openapi.yml"
}

parse_args "$@"
${ARGS["command"]}
