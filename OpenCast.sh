#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="OpenCast"
LOG_DIR="log"
LOG_FILE="$PROJECT_NAME.log"

function is_server_running() {
  lsof -t -i :2020
}

function wait_for_server() {
  while [ ! "$(is_server_running)" ]; do
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
  if [ "$(is_server_running)" ]; then
    echo "$PROJECT_NAME server is already running."
    return
  fi

  if [[ "$1" == "-u" ]]; then
    update
  fi

  cd "$PROJECT_DIR" || exit 1
  mkdir -p "$LOG_DIR"

  echo "Starting $PROJECT_NAME server."
  pipenv run python -m "$PROJECT_NAME" &

  wait_for_server
  pid="$(pgrep -f "python -m $PROJECT_NAME")"
  echo "$pid" >"$PROJECT_DIR/$PROJECT_NAME.pid"
}

function stop() {
  echo "Killing $PROJECT_NAME..."
  lsof -t -i :2020 | xargs kill >/dev/null 2>&1
  sudo killall omxplayer.bin >/dev/null 2>&1
  echo "Done."
}

function restart() {
  stop && start
}

function update() {
  echo "Checking for updates."

  (cd "$PROJECT_DIR" && git pull && pipenv update)
}

function status() {
  echo -n "$PROJECT_NAME is ... "
  [ "$(lsof -t -i :2020)" ] && echo "UP" || echo "DOWN"
}

function logs() {
  tail -n 50 -f "$PROJECT_DIR/$LOG_DIR/$LOG_FILE"
}

function tests() {
  cd "$PROJECT_DIR" || exit 1
  pipenv run python -m unittest discover -v -p "*_test.py"
}

COMMANDS=("start" "stop" "restart" "update" "status" "logs" "tests")
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
