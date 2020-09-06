#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"

#### CLI handlers

spec() {
  jenv "speccy --config $ROOT/specs/.speccy.yml serve $ROOT/specs/openapi.yml"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [spec]="View specifications in beautiful human readable documentation."
)
make_cli default_help_display COMMANDS "$@"
