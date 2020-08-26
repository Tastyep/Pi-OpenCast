#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
WEBAPP_DIR="$ROOT/webapp"
WEBAPP_PORT="8081"
SERVICE_NAME="front"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"
source "$ROOT/script/logging.sh"

#### CLI handlers

function start() {
  local -a params
  params=("--dev")
  expect_params params "start" "$@"

  local npm_cmd
  npm_cmd="WEBAPP_PORT=$WEBAPP_PORT npm run serve &"
  [[ "$1" == "--dev" ]] && npm_cmd="npm start"

  (cd "$WEBAPP_DIR" && eval "$npm_cmd")
}

function stop() {
  (cd "$WEBAPP_DIR" && npm stop)
}

function restart() {
  stop "$@" && start "$@"
}

function status() {
  local status

  status=1
  [[ "$(lsof -t -a -i ":$WEBAPP_PORT" -c node)" ]] && status=0
  log_status "$SERVICE_NAME" "$status"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [start]="Start the service."
  [stop]="Stop the service."
  [restart]="Restart the service."
  [status]="Display the status of the service."
)
make_cli default_help_display COMMANDS "$@"
