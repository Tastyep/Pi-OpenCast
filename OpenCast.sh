#!/usr/bin/env bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="OpenCast"

API_PORT="2020"
WEBAPP_PORT="8081"

LOG_DIR="log"
DOC_DIR="docs"
TEST_DIR="test"
WEBAPP_DIR="webapp"

LOG_FILE="$PROJECT_NAME.log"

source "$PROJECT_DIR/script/cli_builder.sh"
source "$PROJECT_DIR/script/env.sh"

#### CLI handlers

function test() {
  cd "$PROJECT_DIR" || exit 1
  if [ -z "$1" ]; then
    penv python -m unittest discover -v
  else
    local selector="$1"

    if [[ "$selector" != "$TEST_DIR"* ]]; then
      selector="$TEST_DIR.$selector"
    fi
    penv python -m unittest "$selector"
  fi
}

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

#### Internal functions

function is_port_bound() {
  lsof -t -a -i ":$1" -c python
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [format]="Format source code."
  [gen]="Generate content."
  [lint]="Run linters on given targets."
  [service]="Operate services."
  [test]="Run the test suite."
)
make_cli default_help_display COMMANDS "$@"
