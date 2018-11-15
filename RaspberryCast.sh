#!/bin/bash

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="log"
LOG_FILE="$(basename $ROOT).log"

function start() {
  if [ "$(lsof -t -i :2020)" ]; then
    echo "RaspberryCast server is already running."
    return
  fi
  echo "Checking for updates."

  cd "$ROOT"

  git pull
  mkdir -p "$LOG_DIR"
  pipenv install --skip-lock
  echo "Starting RaspberryCast server."
  pipenv run "./server.py" &
  echo "Done."

}

function stop() {
  echo "Killing RaspberryCast..."
  lsof -t -i :2020 | xargs kill >/dev/null 2>&1
  sudo killall omxplayer.bin >/dev/null 2>&1
  echo "Done."
}

function restart() {
  stop && start
}

function status() {
  echo -n "RaspberryCast is ... "
  [ "$(lsof -t -i :2020)" ] && echo "UP" || echo "DOWN"
}

function logs() {
  tail -n 50 -f "$ROOT/$LOG_DIR/$LOG_FILE"
}

if [ "$(id -u)" = "0" ]; then
  echo "Please start this script without root privileges!"
  echo "Try again without sudo."
  exit 0
fi

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
*)
  echo "Usage: $0 {start|stop|restart|status|logs}"
  ;;
esac
