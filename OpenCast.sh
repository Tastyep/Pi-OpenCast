#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="OpenCast"
PROJECT_API_PORT="2020"
PROJECT_WEBAPP_PORT="8081"
LOG_DIR="log"
DOC_DIR="docs"
LOG_FILE="$PROJECT_NAME.log"
TEST_DIR="test"

function is_port_bound() {
  lsof -t -i ":$1"
}

function wait_for_server() {
  while [ ! "$(is_port_bound $1)" ]; do
    sleep 1
  done
}

function element_in() {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && return 0; done
  return 1
}

function start() {
  if [ "$(is_port_bound $PROJECT_API_PORT)" ]; then
    echo "$PROJECT_NAME server is already running."
    return
  fi

  if [[ "$1" == "-u" ]]; then
    update
  fi

  cd "$PROJECT_DIR" || exit 1
  mkdir -p "$LOG_DIR"

  echo "Starting $PROJECT_NAME server."
  (cd ./webapp && npm install && npm start &)
  wait_for_server "$PROJECT_WEBAPP_PORT"

  run_in_env poetry run python -m "$PROJECT_NAME" &
  pid="$(pgrep -f "python -m $PROJECT_NAME")"
  echo "$pid" >"$PROJECT_DIR/$PROJECT_NAME.pid"
}

function stop() {
  echo "Killing $PROJECT_NAME..."
  # Todo hardcoded port
  lsof -t -i :2020 | xargs kill >/dev/null 2>&1
  lsof -t -i :8081 | xargs kill >/dev/null 2>&1
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
  [ "$(lsof -t -i :2020)" ] && echo "UP" || echo "DOWN"
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

  run_in_env make html
  xdg-open "build/html/index.html"
}

function run_in_env() {
  poetry install
  poetry run "$@"
}

# Source profile file as poetry use it to modify the PATH
# This is likely to be done by the display manager, but not always (lightdm).
source ~/.profile

COMMANDS=("start" "stop" "restart" "update" "status" "logs" "test" "gendoc")
if element_in "$1" "${COMMANDS[@]}"; then
  COMMAND="$1"
  shift

  "$COMMAND" "$@"
else
  echo "Usage: $0 {$(
    IFS='|'
    echo "${COMMANDS[*]}"
  )}"
fi
