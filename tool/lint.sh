#!/usr/bin/env bash
# Usage:
#   ./lint.sh command
#
# Commands:
#   all     Run all linters.
#   python  Run the linter on the python code.
#   shell   Run shellcheck on scripts.
#   spec    Run the linter on the API spec.

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
  python && shell && spec
}

python() {
  penv flake8 "$ROOT/OpenCast" "$ROOT/test" --statistics
  log_status "flake8" "$?"
}

shell() {
  require_shellcheck

  sh_files=()
  sh_dirs=("." "tool" "script")
  for sh_dir in "${sh_dirs[@]}"; do
    local find_opts=()

    [[ "$sh_dir" == "." ]] && find_opts+=("-maxdepth" "1")
    while IFS= read -r -d $'\0'; do
      sh_files+=("$REPLY")
    done < <(find "$ROOT/$sh_dir" "${find_opts[@]}" -name "*.sh" -print0)
  done

  shellcheck -s bash "${sh_files[@]}"
  log_status "shellcheck" "$?"
}

spec() {
  jenv "speccy --config $ROOT/specs/.speccy.yml lint $ROOT/specs/openapi.yml"
  log_status "speccy" "$?"
}

parse_args "$@"
${ARGS["command"]}
