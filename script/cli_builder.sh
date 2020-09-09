#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"

# shellcheck source=script/array.sh
source "$HERE/array.sh"

make_cli() {
  local display_help
  local -n commands

  display_help="$1"
  commands="$2"
  shift 2

  if element_in "$1" "${!commands[@]}"; then
    local cmd="$1"
    shift

    "$cmd" "$@"
  else
    "$display_help" commands
  fi
}

default_help_display() {
  printf "Usage: %s command\n\n" "$0"
  printf "Available commands:\n"

  local -n command_ref
  local longest=0

  command_ref="$1"
  for cmd in "${!command_ref[@]}"; do
    local len="${#cmd}"

    [[ "$len" > "$longest" ]] && longest="$len"
  done

  local sorted_cmds
  mapfile -t sorted_cmds < <(
    for cmd in "${!command_ref[@]}"; do
      printf "%s\n" "$cmd"
    done | sort
  )

  for cmd in "${sorted_cmds[@]}"; do
    local size_diff="$(("$longest" - "${#cmd}"))"
    local spaces=""
    if [[ "$size_diff" -gt 0 ]]; then
      spaces="$(printf ' %.0s' $(seq 1 "$size_diff"))"
    fi
    printf " - %s:%s %s\n" "$cmd" "$spaces" "${command_ref["$cmd"]}"
  done
}

expect_params() {
  local -n params_ref parsed_ref
  local -a params_attr
  local command args count

  params_ref="$1"
  parsed_ref="$2"
  command="$3"
  args=("$@")
  count="${#args[@]}"

  identify_params params_attr

  local matched_params
  matched_params=()
  # Iterate on arguments
  for ((i = 3; i < count; i++)); do
    local arg found index

    arg="${args[$i]}"
    found=0
    for j in "${!params_ref[@]}"; do
      if element_in "$j" "${matched_params[@]}"; then
        continue
      fi
      if [[ "$arg" == "${params_ref["$j"]}" ]]; then
        found=1
        index="$j"
        break
      fi
      if [[ "$found" == "0" && "${params_attr["$j"]}" == *"argument"* ]]; then
        found=1
        index="$j"
      fi
    done
    if [[ "$found" == "0" ]]; then
      printf "%s %s: invalid argument %s\n" "$0" "$command" "$arg"
      display_help
    fi

    local decayed_name

    decayed_name="$(decay "${params_ref["$index"]}" "${params_attr["$index"]}")"
    matched_params+=("$index")
    # Ignore SC2034 since shellcheck doesn't follow references
    # shellcheck disable=SC2034
    parsed_ref["$decayed_name"]="$arg"
  done
  for i in "${!params_ref[@]}"; do
    if [[ "${params_attr["$i"]}" == *"required"* ]] && ! element_in "$i" "${matched_params[@]}"; then
      printf "%s %s: missing required argument %s\n" "$0" "$command" "${params_ref["$i"]}"
      display_help
    fi
  done
}

decay() {
  local param type

  param="$1"
  type="$2"
  IFS='|' read -r -a attrs <<<"$type"
  for attr in "${attrs[@]}"; do
    case "$attr" in
    "optional" | "required" | "argument")
      param="${param:1:${#param}-2}"
      ;;
    esac
  done
  echo "$param"
}

display_help() {
  local script_name

  script_name="$(basename "$0")"
  printf "usage: %s %s" "$script_name" "$command"
  for param in "${params_ref[@]}"; do
    printf " %s" "$param"
  done
  printf "\n"
  exit 1
}

identify_params() {
  local -n attrs_ref

  attrs_ref="$1"
  for param in "${params_ref[@]}"; do
    local attr=""

    [[ "$param" =~ \[.*\] ]] && attr="$attr|optional"
    [[ "$param" =~ \(.*\) ]] && attr="$attr|required"
    [[ "$param" =~ \<.*\> ]] && attr="$attr|argument"
    [[ "$param" =~ --.* ]] && attr="$attr|option"
    attrs_ref+=("$attr")
  done
}
