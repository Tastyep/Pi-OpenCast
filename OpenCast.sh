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

source "$PROJECT_DIR/script/gen_cli.sh"
source "$PROJECT_DIR/script/env.sh"

#### CLI handlers

function start() {
  if [ "$(is_port_bound $API_PORT)" ]; then
    echo "$PROJECT_NAME server is already running."
    return
  fi

  if [[ "$1" == "-u" ]]; then
    update
  fi

  cd "$PROJECT_DIR" || exit 1
  mkdir -p "$LOG_DIR"

  echo "Starting $PROJECT_NAME server."
  (cd "$WEBAPP_DIR" && WEBAPP_PORT=$WEBAPP_PORT npm run serve &)
  run_in_env python -m "$PROJECT_NAME" &
}

function stop() {
  echo "Killing $PROJECT_NAME..."
  # Todo hardcoded port
  lsof -t -a -i ":$API_PORT" -c python | xargs kill >/dev/null 2>&1
  (cd "$PROJECT_DIR/$WEBAPP_DIR" && npm stop)
  echo "Done."
}

function restart() {
  stop && start ""
}

function update() {
  echo "Checking for updates."

  (cd "$PROJECT_DIR" && poetry update)
}

function status() {
  echo -n "$PROJECT_NAME is ... "
  [ "$(lsof -t -a -i ":$API_PORT" -c python)" ] && echo "UP" || echo "DOWN"
}

function logs() {
  tail -n 50 -f "$PROJECT_DIR/$LOG_DIR/$LOG_FILE"
}

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

function gendoc() {
  cd "$DOC_DIR" || exit 1

  penv make html -b coverage
  xdg-open "build/html/index.html"
}

function gen() {
  "$PROJECT_DIR/tool/generate.sh" "$@"
}

function lint() {
  "$PROJECT_DIR/tool/lint.sh" "$@"
}

#### Internal functions

function is_port_bound() {
  lsof -t -a -i ":$1" -c python
}

declare -A COMMANDS
COMMANDS=(
  [gen]="Generate content."
  [lint]="Run linters on given targets."
  [logs]="Tail the log file."
  [restart]="Restart $PROJECT_NAME."
  [start]="Start $PROJECT_NAME."
  [status]="Print the operational status of $PROJECT_NAME."
  [stop]="Stop $PROJECT_NAME."
  [test]="Run the test suite."
  [update]="Update $PROJECT_NAME."
)
make_basic_cli default_help_display COMMANDS "$@"
