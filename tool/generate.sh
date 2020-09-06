#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"

#### CLI handlers

doc() {
  (cd "$ROOT/docs" && penv make clean && penv make html -b coverage)
}

spec() {
  mkdir -p "$ROOT/gen"
  jenv "speccy --config $ROOT/specs/.speccy.yml resolve $ROOT/specs/openapi.yml --output $ROOT/gen/openapi.yml"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [doc]="Generate documentation files."
  [spec]="Generate a merged openapi file."
)
make_cli default_help_display COMMANDS "$@"
