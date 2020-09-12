#!/usr/bin/env bash
# Usage:
#   ./generate.sh command
#
# Commands:
#   doc   Generate documentation files.
#   spec  Generate a merged openapi file.

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

spec() {
  mkdir -p "$ROOT/gen"
  jenv "speccy --config $ROOT/specs/.speccy.yml resolve $ROOT/specs/openapi.yml --output $ROOT/gen/openapi.yml"
}

parse_args "$@"
${ARGS["command"]}
