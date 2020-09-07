#!/usr/bin/env bash

HERE="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/env.sh
source "$ROOT/script/env.sh"
# shellcheck source=script/logging.sh
source "$ROOT/script/logging.sh"
# shellcheck source=script/deps.sh
source "$ROOT/script/deps.sh"

#### CLI handlers

all() {
  python "$@"
  shell "$@"
}

python() {
  # shellcheck disable=SC2034
  local -a params=("--check")
  local -A parsed
  expect_params params parsed "python" "$@"

  local black_opts isort_opts=()
  if [[ -n "${parsed["--check"]}" ]]; then
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

  # shellcheck disable=SC2034
  local -a params=("--check")
  local -A parsed
  expect_params params parsed "shell" "$@"

  local shfmt_opts=("-l" "-d" "-i" "2")
  [[ -z "${parsed["--check"]}" ]] && shfmt_opts+=("-w")

  sh_files=()
  sh_dirs=("." "tool" "script")
  for sh_dir in "${sh_dirs[@]}"; do
    local find_opts=()

    [[ "$sh_dir" == "." ]] && find_opts+=("-maxdepth" "1")
    while IFS= read -r -d $'\0'; do
      sh_files+=("$REPLY")
    done < <(find "$ROOT/$sh_dir" "${find_opts[@]}" -name "*.sh" -print0)
  done

  shfmt "${shfmt_opts[@]}" "${sh_files[@]}"
  log_status "shfmt" "$?"
}

#### Internal functions

display_formatter_status() {
  local name status marker

  name="$1"
  status="$2"
  [[ "$status" == "1" ]] && marker="✗" || marker="✓"

  printf "%s %s\n" "$marker" "$name"
  return "$status"
}

#### CLI definition

declare -A COMMANDS
export COMMANDS=(
  [all]="Run all formatters."
  [python]="Run formatters on python code."
  [shell]="Run formatters on shell code."
)
make_cli default_help_display COMMANDS "$@"
