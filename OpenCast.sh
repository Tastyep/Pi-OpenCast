#!/usr/bin/env bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

source "$PROJECT_DIR/script/cli_builder.sh"

#### CLI handlers

format() {
  "$PROJECT_DIR/tool/format.sh" "$@"
}

gen() {
  "$PROJECT_DIR/tool/generate.sh" "$@"
}

lint() {
  "$PROJECT_DIR/tool/lint.sh" "$@"
}

serve() {
  "$PROJECT_DIR/tool/serve.sh" "$@"
}

service() {
  "$PROJECT_DIR/tool/service.sh" "$@"
}

test() {
  "$PROJECT_DIR/tool/test.sh" "$@"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [format]="Format source code."
  [gen]="Generate content."
  [lint]="Run linters on given targets."
  [serve]="Serve static web pages."
  [service]="Operate services."
  [test]="Run the test suite of a service."
)
make_cli default_help_display COMMANDS "$@"
