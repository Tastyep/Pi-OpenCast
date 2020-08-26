#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
PROJECT_NAME="OpenCast"
API_PORT="2020"
LOG_DIR="log"
LOG_FILE="$PROJECT_NAME.log"
SERVICE_NAME="back"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"
source "$ROOT/script/logging.sh"

#### CLI handlers

function log() {
  tail -n 50 -f "$ROOT/$LOG_DIR/$LOG_FILE"
}

function start() {
  mkdir -p "$LOG_DIR"
  penv python -m "$PROJECT_NAME" &
}

function stop() {
  echo "Killing $PROJECT_NAME..."
  lsof -t -a -i ":$API_PORT" -c python | xargs kill >/dev/null 2>&1
  echo "Done."
}

function restart() {
  stop && start ""
}

function status() {
  local status

  status=1
  [[ "$(lsof -t -a -i ":$API_PORT" -c python)" ]] && status=0
  log_status "$SERVICE_NAME" "$status"
}

function update() {
  echo "Checking for updates."

  poetry update
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [log]="Tail the log file."
  [start]="Start the service."
  [stop]="Stop the service."
  [restart]="Restart the service."
  [status]="Display the status of the service."
  [update]="Update the dependencies of the service."
)
make_cli default_help_display COMMANDS "$@"
