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
  local options
  local node_version

  node_version="$(node --version | cut -f 1 -d'.' | tr -d 'v')"
  [[ "$node_version" -ge "17" ]] && options="NODE_OPTIONS=--openssl-legacy-provider"

  (cd "$ROOT/webapp" && eval "$options npm run build")
}

parse_args "$@"
${ARGS["command"]}
