#!/usr/bin/env bash

function log_status() {
  local name status marker

  name="$1"
  status="$2"
  [[ "$status" == "1" ]] && marker="✗" || marker="✓"

  printf "$marker $name\n"
  return "$status"
}
