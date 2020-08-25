#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"
source "$ROOT/script/logging.sh"

#### CLI handlers

function all() {
  python "$@"
}

function python() {
  local black_opts isort_opts=()
  local -a params

  params=("--check")
  expect_params params "python" "$@"
  if [[ "$1" == "--check" ]]; then
    black_opts+=("--check")
    isort_opts+=("--check-only")
  fi
  # Collect python files
  local py_files

  py_files=()
  while IFS= read -r -d $'\0'; do
    py_files+=("$REPLY")
  done < <(find "$ROOT/OpenCast" -name "*.py" -print0)

  penv black "${black_opts[@]}" "${py_files[@]}"
  log_status "black" "$?"
  penv isort "${isort_opts[@]}" "${py_files[@]}"
  log_status "isort" "$?"
}

#### Internal functions

function display_formatter_status() {
  local name status marker

  name="$1"
  status="$2"
  [[ "$status" == "1" ]] && marker="✗" || marker="✓"

  printf "$marker $name\n"
  return "$status"
}

#### CLI definition

declare -A COMMANDS
COMMANDS=(
  [all]="Run all formatters."
  [python]="Run formatters on the python code."
)
make_cli default_help_display COMMANDS "$@"
