#!/usr/bin/env bash
# Usage:
#   ./service-front.sh command [--dev]
#
# Commands:
#   start    Start the service.
#   stop     Stop the service.
#   restart  Restart the service.
#   status   Display the status of the service.
#
# Options:
#   --dev  Start the service in development mode.

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
WEBAPP_DIR="$ROOT/webapp"
WEBAPP_PORT="8081"
SERVICE_NAME="front"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/logging.sh
source "$ROOT/script/logging.sh"
# shellcheck source=script/env.sh
source "$ROOT/script/env.sh"

#### CLI handlers

start() {
  local npm_cmd
  npm_cmd="WEBAPP_PORT=$WEBAPP_PORT npm run serve &"
  [[ -n "${ARGS["--dev"]}" ]] && npm_cmd="npm start"

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

parse_args "$@"
${ARGS["command"]}
