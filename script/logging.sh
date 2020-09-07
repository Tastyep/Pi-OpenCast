#!/usr/bin/env bash

log_status() {
  local name status marker

  name="$1"
  status="$2"
  [[ "$status" == "1" ]] && marker="✗" || marker="✓"

  printf "%s %s\n" "$marker" "$name"
  return "$status"
}
