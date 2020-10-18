#!/usr/bin/env bash

NOCOLOR="\\033[0m"
YELLOW_COL="\\033[1;33m"
RED_COL="\\033[1;31m"
GREEN_COL="\\033[1;32m"

# Display colorized text
colorize() {
  local color="$1"
  local text="$2"
  printf "%b%s%b" "${color}" "${text}" "${NOCOLOR}"
}

# Log an info message.
log_info() {
  printf "%s %s\n" "$(colorize "$YELLOW_COL" ">>")" "$1"
}

# Log an error message and exit.
log_error() {
  printf "%s %s\n" "$(colorize "$RED_COL" "!!")" "$1"
  exit 1
}

log_status() {
  local name status marker

  name="$1"
  status="$2"
  [[ "$status" == "0" ]] && marker="$(colorize "$GREEN_COL" "✓")" || marker="$(colorize "$RED_COL" "✗")"

  printf "%s %s\n" "$marker" "$name"
  return "$status"
}
