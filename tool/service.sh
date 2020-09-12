#!/usr/bin/env bash
# Usage:
#   ./service.sh command [<args>...]
#
# Commands:
#   back     Command the back-end service.
#   front    Command the front-end service.
#   start    Start all services.
#   stop     Stop all services.
#   restart  Restart all services.
#   status   Display the status of all service.

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SERVICE_BACK="$HERE/service-back.sh"
SERVICE_FRONT="$HERE/service-front.sh"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"

#### CLI handlers

back() {
  "$SERVICE_BACK" "$@"
}

front() {
  "$SERVICE_FRONT" "$@"
}

start() {
  "$SERVICE_BACK" "start" "$@" &&
    "$SERVICE_FRONT" "start" "$@"
}

stop() {
  "$SERVICE_BACK" "stop" "$@" &&
    "$SERVICE_FRONT" "stop" "$@"
}

restart() {
  "$SERVICE_BACK" "restart" "$@" &&
    "$SERVICE_FRONT" "restart" "$@"
}

status() {
  "$SERVICE_BACK" "status"
  "$SERVICE_FRONT" "status"
}

parse_args "$@"
IFS=";" read -r -a arguments <<<"${ARGS["args"]}"
${ARGS["command"]} "${arguments[@]}"
