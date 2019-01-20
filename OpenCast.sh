#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="OpenCast"
LOG_DIR="log"
LOG_FILE="$PROJECT_NAME.log"

function start() {
  if [ "$(lsof -t -i :2020)" ]; then
    echo "$PROJECT_NAME server is already running."
    return
  fi

  echo "Checking for updates."
  cd "$PROJECT_DIR" || exit 1

  git pull
  mkdir -p "$LOG_DIR"
  echo "Starting $PROJECT_NAME server."
  pipenv run python -m "$PROJECT_NAME" &
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

case "$1" in
start)
  start
  ;;
stop)
  stop
  ;;
restart)
  restart
  ;;
status)
  status
  ;;
logs)
  logs
  ;;
test)
  tests
  ;;
*)
  echo "Usage: $0 {start|stop|restart|status|logs|test}"
  ;;
esac
