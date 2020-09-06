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

start() {
  local -a params
  local -A parsed
  params=("--dev")
  expect_params params parsed "start" "$@"

  local npm_cmd
  npm_cmd="WEBAPP_PORT=$WEBAPP_PORT npm run serve &"
  [[ ! -z "${parsed["--dev"]}" ]] && npm_cmd="npm start"

  (cd "$WEBAPP_DIR" && eval "$npm_cmd")
}

stop() {
  (cd "$WEBAPP_DIR" && npm stop)
}

restart() {
  stop "$@" && start "$@"
}

status() {
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
