#!/usr/bin/env bash
# Usage:
#   ./service-back.sh command
#
# Commands:
#   log      Tail the log file.
#   start    Start the service.
#   stop     Stop the service.
#   restart  Restart the service.
#   status   Display the status of the service.

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
PROJECT_NAME="OpenCast"
API_PORT="$(grep "port:" <"$ROOT/config.yml" | cut -d':' -f2 | xargs)"
LOG_DIR="log"
LOG_FILE="$PROJECT_NAME.log"
SERVICE_NAME="back"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/env.sh
source "$ROOT/script/env.sh"
# shellcheck source=script/logging.sh
source "$ROOT/script/logging.sh"

#### CLI handlers

log() {
  tail -n 50 -f "$ROOT/$LOG_DIR/$LOG_FILE"
}

start() {
  mkdir -p "$ROOT/$LOG_DIR"
  penv python -m "$PROJECT_NAME" &
}

stop() {
  log_info "Killing $PROJECT_NAME..."
  lsof -t -a -i ":$API_PORT" -c python | xargs kill >/dev/null 2>&1
  log_info "Done."
}

restart() {
  stop && start
}

status() {
  local status

  status=1
  [[ "$(lsof -t -a -i ":$API_PORT" -c python)" ]] && status=0
  log_status "$SERVICE_NAME" "$status"
}

parse_args "$@"
${ARGS["command"]}
