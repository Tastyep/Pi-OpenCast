#!/usr/bin/env bash
# Usage:
#   ./OpenCast.sh command [<args>...]
#
# Commands:
#   deps     Interact with dependencies.
#   format   Run formatters on the source code.
#   generate Generate content.
#   lint     Lint the source code.
#   service  Operate services.
#   test     Run the tests.

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Source profile file as poetry and nvm use it to modify the PATH
# This is likely to be done by the display manager, but not always (lightdm).
# shellcheck source=/dev/null
source ~/.profile

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"

parse_args "$@"
IFS=";" read -r -a arguments <<<"${ARGS["args"]}"
"$ROOT/tool/${ARGS["command"]}.sh" "${arguments[@]}"
