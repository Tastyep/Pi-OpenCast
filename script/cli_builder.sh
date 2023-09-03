#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"

# shellcheck source=script/array.sh
source "$HERE/array.sh"

# Map exposed to user
declare -A ARGS

parse_args() {
  local -a usage
  local -a commands
  local -A options
  local -a params
  local -A params_type
  local -A params_attr

  # Read the usage
  while IFS= read -r line; do
    [[ -z "$line" ]] && break
    [[ "$line" == "#!"* ]] && continue
    usage+=("${line/\#/}")
  done <"$0"

  parse_sections
  parse_arguments "$@"
}

parse_sections() {
  local section=""

  for line in "${usage[@]}"; do
    local lwc_line="${line,,}"
    [[ "${lwc_line}" == *"usage:"* ]] && section="usage" && continue
    [[ "${lwc_line}" == *"commands:"* ]] && section="commands" && continue
    [[ "${lwc_line}" == *"options:"* ]] && section="options" && continue
    [[ -z "$section" ]] && continue

    case "$section" in
    "usage")
      parse_usage_section "$line"
      ;;
    "commands")
      parse_commands_section "$line"
      ;;
    "options")
      parse_options_section "$line"
      ;;
    esac

  done
}

parse_usage_section() {
  local line="$1"

  # Clean line to extract params
  line="${line#"${line%%[![:space:]]*}"}"

  # Read params into an array
  read -ra usage_params <<<"$line"
  local count="${#usage_params[@]}"

  for ((i = 1; i < count; i++)); do
    local param="${usage_params["$i"]}"
    local decayed_param

    decayed_param="$(decay "$param")"
    ARGS["$decayed_param"]=""
    params+=("$decayed_param")
    params_type["$decayed_param"]="$(param_type "$param")"
    params_attr["$decayed_param"]="$(param_attr "$param")"
    # shellcheck disable=SC2034
    [[ "${params_type["$decayed_param"]}" == "option" ]] && options["$decayed_param"]=""
  done
}

parse_commands_section() {
  local line="$1"

  # Clean line from spaces to extract commands
  line="${line#"${line%%[![:space:]]*}"}"

  # Read command desc into an array
  read -ra words <<<"$line"
  commands+=("${words[0]}")
}

parse_options_section() {
  local line="$1"
  local opts help_msg

  # Clean line from spaces to extract options
  line="${line#"${line%%[![:space:]]*}"}"
  help_msg="${line#*"  "}"
  opts="${line%"  "*}"

  if [[ -z "$opts" ]]; then
    printf "Error: invalid option format '%s'.\n" "$line"
    exit 1
  fi

  if [[ "$opts" == "$help_msg" ]]; then
    printf "Error: can't parse help message for '%s'.\nOptions and descriptions should be separated by 2 spaces.\n" "$opts"
    exit 1
  fi

  # Trim all white spaces
  opts="${opts## }"
  opts="${opts%% }"

  local long_opt

  # Replace commas with space to make it iterable
  opts=${opts//,/ }

  # Note: change this to add support for valued options
  # Partial support for short options, see resolve_option
  long_opt="${opts##* }"
  for opt in $opts; do
    if [[ "$opt" == "$long_opt" ]]; then
      options["$opt"]="" # empty string signals that it's the used option.
    else
      options["$opt"]="$long_opt" # short options point to the long one
      unset 'ARGS["$opt"]'          # remove entry as long options are used
    fi
  done
}

parse_arguments() {
  local args=("$@")
  local count="${#args[@]}"
  local param_idx=0
  local param_count="${#params[@]}"

  if element_in "--help" "${args[@]}"; then
    print_usage
  fi

  for ((i = 0; i < count && param_idx < param_count; i++)); do
    local arg="${args["$i"]}"
    local param="${params["$param_idx"]}"
    local param_type="${params_type["$param"]}"
    local param_attr="${params_attr["$param"]}"

    # echo "arg: $arg, param: $param, param_type $param_type"
    if [[ "$(param_type "$arg")" == "option" ]]; then
      parse_option_arg "$arg"
    elif [[ "$param_type" == "command" ]]; then
      parse_command_arg "$arg"
    else
      parse_arg "$arg"
    fi
  done

  if [[ "$i" -lt "$count" ]]; then
    printf "Error: could not match arguments:"
    for (( ; i < count; i++)); do
      printf " %s" "${args["$i"]}"
    done
    printf "\n"
    print_usage
  fi

  for param in "${params[@]}"; do
    local param_attr="${params_attr["$param"]}"

    if [[ -z "${ARGS["$param"]}" && "$param_attr" == *"required"* ]]; then
      printf "Error: missing required argument '%s'.\n" "$param"
      print_usage
    fi
  done
}

# Only support long options without arguments
parse_option_arg() {
  local arg="$1"

  if [[ ("$param_attr" == *"repeating"*) ]]; then
    assign_repeating_arg
  else
    # First condition refers to options only listed in the Usage section
    if ! element_in "$arg" "${!ARGS[@]}" && ! element_in "$arg" "${!options[@]}"; then
      printf "Error: invalid option: '%s'.\n" "$arg"
      print_usage
    fi
    local long_opt
    long_opt="$(resolve_option "$arg")"
    ARGS["$long_opt"]=true
  fi
}

# Resolve short options into long ones when available
resolve_option() {
  local opt="$1"

  if ! element_in "$opt" "${options[@]}"; then
    echo "$opt"
    return
  fi
  while [[ -n "${options["$opt"]}" ]]; do
    opt="${options["$opt"]}"
  done
  echo "$opt"
}

parse_command_arg() {
  local arg="$1"

  if ! element_in "$arg" "${commands[@]}"; then
    printf "Error: invalid command %s.\n" "$arg"
    print_usage
  fi
  ARGS["$param"]="$arg"
  [[ "$param_attr" != *"repeating"* ]] && param_idx=$((param_idx + 1))
}

parse_arg() {
  local arg="$1"

  if [[ ("$param_attr" == *"repeating"*) ]]; then
    assign_repeating_arg
  else
    ARGS["$param"]="$arg"
    param_idx=$((param_idx + 1))
  fi
}

assign_repeating_arg() {
  if [[ -n "${ARGS["$param"]}" ]]; then
    ARGS["$param"]="${ARGS["$param"]};$arg"
  else
    ARGS["$param"]="$arg"
  fi
}

print_usage() {
  local min_space="${#usage}"

  for line in "${usage[@]}"; do
    local trimed_line="${line#"${line%%[![:space:]]*}"}"
    [[ -z "$trimed_line" ]] && continue

    local len="$((${#line} - ${#trimed_line}))"
    [[ "$len" -lt "$min_space" ]] && min_space="$len"
  done

  for line in "${usage[@]}"; do
    printf "%s\n" "${line:$min_space:${#line}}"
  done
  exit 1
}

# param types:
# <> argument
# -- option
# command
#
# param attr
# [] optional
# () required
# ... repeating

param_type() {
  local param="$1"

  if [[ "$param" =~ \<.*\> ]]; then
    echo "argument"
    return
  fi
  if [[ "$param" =~ --.* ]]; then
    echo "option"
    return
  fi
  echo "command"
}

param_attr() {
  local param="$1"
  local attr=""

  [[ "$param" =~ \[.*\] ]] && attr="$attr|optional"
  [[ "$param" =~ \(.*\) ]] && attr="$attr|required"
  [[ "$param" =~ [^\.]*\.{3} ]] && attr="$attr|repeating"
  [[ "$attr" != *"optional"* && "$attr" != *"required"* ]] && attr="$attr|required"

  echo "$attr"
}

decay() {
  local param="$1"
  local decayed=true

  while "$decayed"; do
    local copy="$param"

    [[ "$param" =~ ^\[.*\]$ ]] && param="${param:1:${#param}-2}"
    [[ "$param" =~ ^\<.*\>$ ]] && param="${param:1:${#param}-2}"
    [[ "$param" =~ [^\.]*\.{3} ]] && param="${param:0:${#param}-3}"
    [[ "$param" == "$copy" ]] && decayed=false
  done

  echo "$param"
}
