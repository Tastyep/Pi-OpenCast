#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"

source "$HERE/array.sh"

function make_cli() {
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

function expect_params() {
  local -n params_ref
  local command
  local args
  local count

  params_ref="$1"
  command="$2"
  args=("$@")
  count="${#args[@]}"
  for ((i = 2; i < count; i++)); do
    local param

    param="${args[$i]}"
    if ! element_in "$param" "${params_ref[@]}"; then
      printf "$0 $command: invalid argument $param\n"
      printf "usage: $command "
      for param in "$params_ref"; do
        printf "[$param]"
      done
      printf "\n"
      exit 1
    fi
  done
}
