#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

source "$ROOT/script/cli_builder.sh"
source "$ROOT/script/env.sh"
source "$ROOT/script/logging.sh"

#### CLI handlers

all() {
  python "$@"
}

python() {
  local -a params
  local -A parsed
  params=("--check")
  expect_params params parsed "python" "$@"

  local black_opts isort_opts=()
  if [[ ! -z "${parsed["--check"]}" ]]; then
    black_opts+=("--check")
    isort_opts+=("--check-only")
  fi
  # Collect python files
  local py_files
  local -a py_dirs

  py_files=()
  py_dirs=("OpenCast" "test")
  for py_dir in "${py_dirs[@]}"; do
    while IFS= read -r -d $'\0'; do
      py_files+=("$REPLY")
    done < <(find "$ROOT/$py_dir" -name "*.py" -print0)
  done

  penv black "${black_opts[@]}" "${py_files[@]}"
  log_status "black" "$?"
  penv isort "${isort_opts[@]}" "${py_files[@]}"
  log_status "isort" "$?"
}

shell() {
  require_go
  require_shfmt

  local -a params
  local -A parsed
  params=("--check")
  expect_params params parsed "shell" "$@"

  local shfmt_opts=("-l" "-d" "-s")
  [[ -z "${parsed["--check"]}" ]] && shfmt_opts+=("-w")

  sh_files=()
  sh_dirs=("" "tool" "script")
  for sh_dir in "${sh_dirs[@]}"; do
    while IFS= read -r -d $'\0'; do
      sh_files+=("$REPLY")
    done < <(find "$ROOT/$sh_dir" -name "*.sh" -print0)
  done

  shfmt "${shfmt_opts[@]}" "${sh_files[@]}"
}

#### Internal functions

display_formatter_status() {
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
  [python]="Run formatters on python code."
  [shell]="Run formatters on shell code."
)
make_cli default_help_display COMMANDS "$@"
