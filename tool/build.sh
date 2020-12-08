#!/usr/bin/env bash
# Usage:
#   ./build.sh command
#
# Commands:
#   doc      Generate documentation files.
#   webapp   Generate a production build of the webapp.

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

webapp() {
  (cd "$ROOT/webapp" && npm run build)
}

parse_args "$@"
${ARGS["command"]}
