#!/usr/bin/env bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

source "$PROJECT_DIR/script/cli_builder.sh"

#### CLI handlers

function format() {
  "$PROJECT_DIR/tool/format.sh" "$@"
}

function gen() {
  "$PROJECT_DIR/tool/generate.sh" "$@"
}

function lint() {
  "$PROJECT_DIR/tool/lint.sh" "$@"
}

function service() {
  "$PROJECT_DIR/tool/service.sh" "$@"
}

function test() {
  "$PROJECT_DIR/tool/test.sh" "$@"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [format]="Format source code."
  [gen]="Generate content."
  [lint]="Run linters on given targets."
  [service]="Operate services."
  [test]="Run the test suite of a service."
)
make_cli default_help_display COMMANDS "$@"
