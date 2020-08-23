#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$HERE/array.sh"

function make_basic_cli() {
  local display_help
  local -n commands

  display_help="$1"
  commands="$2"
  shift 2
  local args="$@"

  if element_in "$1" "${!commands[@]}"; then
    local cmd="$1"
    shift

    "$cmd" "$@"
  else
    "$display_help" commands
  fi
}

function default_help_display() {
  printf "Usage: $0 command\n\n"
  printf "Available commands:\n"

  local -n command_ref
  local longest=0

  command_ref="$1"
  for cmd in "${!command_ref[@]}"; do
    local len="${#cmd}"

    [[ "$len" > "$longest" ]] && longest="$len"
  done

  local sorted_cmds=$(
    for cmd in "${!command_ref[@]}"; do
      printf "$cmd\n"
    done | sort
  )

  for cmd in ${sorted_cmds[@]}; do
    local size_diff="$(("$longest" - "${#cmd}"))"
    local spaces=""
    if [[ "$size_diff" > 0 ]]; then
      spaces="$(printf ' %.0s' $(seq 1 "$size_diff"))"
    fi
    printf " - $cmd:$spaces ${command_ref["$cmd"]}\n"
  done
}
