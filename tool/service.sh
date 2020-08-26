#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SERVICE_BACK="$HERE/service-back.sh"
SERVICE_FRONT="$HERE/service-front.sh"

source "$ROOT/script/cli_builder.sh"

#### CLI handlers

function back() {
  "$SERVICE_BACK" "$@"
}

function front() {
  "$SERVICE_FRONT" "$@"
}

function start() {
  "$SERVICE_BACK" "start" "$@" &&
    "$SERVICE_FRONT" "start" "$@"
}

function stop() {
  "$SERVICE_BACK" "stop" "$@" &&
    "$SERVICE_FRONT" "stop" "$@"
}

function restart() {
  "$SERVICE_BACK" "restart" "$@" &&
    "$SERVICE_FRONT" "restart" "$@"
}

function status() {
  "$SERVICE_BACK" "status" "$@"
  "$SERVICE_FRONT" "status" "$@"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [back]="Back end service."
  [front]="Front end service."
  [start]="Start all services."
  [stop]="Stop all services."
  [restart]="Restart all services."
  [status]="Display the status of all service."
)
make_cli default_help_display COMMANDS "$@"
