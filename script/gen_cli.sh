#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$HERE/array.sh"

function make_basic_cli() {
  local -n commands

  commands="$1"
  shift
  local args="$@"

  if element_in "$1" "${!commands[@]}"; then
    local cmd="$1"
    shift

    "$cmd" "$@"
  else
    display_help $commands
  fi
}

function display_help() {
  printf "Usage: $0:\n\n"
  printf "Available commands:\n"

  # Append a default the help command entry
  commands[help]="Display this help message."

  local longest=0
  for cmd in "${!commands[@]}"; do
    local len="${#cmd}"

    [[ "$len" > "$longest" ]] && longest="$len"
  done

  local sorted_cmds=$(
    for cmd in "${!commands[@]}"; do
      printf "${commands[$cmd]}:::$cmd\n"
    done | sort | awk -F::: '{print $2}'
  )

  for cmd in ${sorted_cmds[@]}; do
    local size_diff="$(("$longest" - "${#cmd}"))"
    local spaces=""
    if [[ "$size_diff" > 0 ]]; then
      spaces="$(printf ' %.0s' $(seq 1 "$size_diff"))"
    fi
    printf " - $cmd:$spaces ${commands["$cmd"]}\n"
  done
}
