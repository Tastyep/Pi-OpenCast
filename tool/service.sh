#!/usr/bin/env bash

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

test() {
  "$SERVICE_BACK" "test" &&
    "$SERVICE_FRONT" "test"
}

#### CLI definition

declare -A COMMANDS
export COMMANDS=(
  [back]="Back end service."
  [front]="Front end service."
  [start]="Start all services."
  [stop]="Stop all services."
  [restart]="Restart all services."
  [status]="Display the status of all service."
  [test]="Run tests for all services."
)
make_cli default_help_display COMMANDS "$@"
