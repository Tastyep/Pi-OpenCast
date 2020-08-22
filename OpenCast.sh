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

function is_port_bound() {
  lsof -t -a -i ":$1" -c python
}

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
  run_in_env poetry run python -m "$PROJECT_NAME" &
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
    run_in_env python -m unittest discover -v
  else
    local selector="$1"

    if [[ "$selector" != "$TEST_DIR"* ]]; then
      selector="$TEST_DIR.$selector"
    fi
    run_in_env python -m unittest "$selector"
  fi
}

function gendoc() {
  cd "$DOC_DIR" || exit 1

  run_in_env make html -b coverage
  xdg-open "build/html/index.html"
}

function run_in_env() {
  poetry install
  poetry run "$@"
}

# Source profile file as poetry use it to modify the PATH
# This is likely to be done by the display manager, but not always (lightdm).
source ~/.profile

declare -A COMMANDS
COMMANDS=(
  [start]="Start $PROJECT_NAME."
  [stop]="Stop $PROJECT_NAME."
  [restart]="Restart $PROJECT_NAME."
  [update]="Update $PROJECT_NAME."
  [status]="Print the operational status of $PROJECT_NAME."
  [logs]="Tail the log file."
  [test]="Run the test suite."
  [gendoc]="Generate local documentation."
)
make_basic_cli COMMANDS "$@"
