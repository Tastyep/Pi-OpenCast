#!/usr/bin/env bash
# Usage:
#   ./setup.sh [--ci]
#
# Options:
#   --ci  Remove dependency checks for vlc and ffmpeg

ROOT="$(cd "$(dirname "${BASH_SOURCE:-0}")" && pwd)"
USER="$(whoami)"
PROJECT="$(basename "$ROOT")"
INTERNAL_NAME="$(echo "$PROJECT" | cut -f2 -d'-')"
SYSTEMD_CONFIG_DIR="/etc/systemd/system/"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/logging.sh
source "$ROOT/script/logging.sh"

# Install system dependencies.
check_system_deps() {
  log_info "Checking system dependencies..."
  local -a deps=("curl" "lsof" "python" "python3" "pip3" "node" "npm")
  local status fail
  [[ "${ARGS["--ci"]}" == false ]] && deps+=("ffmpeg" "vlc")

  fail=false
  for dep in "${deps[@]}"; do
    command -v "$dep" &>/dev/null
    status="$?"
    [[ "$status" = "1" ]] && fail=true
    log_status "$dep" "$status"
  done

  if [[ "$fail" = true ]]; then
    log_error "Missing dependencies, please install them."
    exit 1
  fi
}

# Install project dependencies.
install_project_deps() {
  log_info "Installing project dependencies..."

  curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" | python3
  "$ROOT/$INTERNAL_NAME.sh" service back update
  (cd "$ROOT/webapp" && npm install)
}

# Format and install the systemd config file.
start_at_boot() {
  log_info "Setting up startup at boot"

  local service_name config
  # lowercase
  service_name="${INTERNAL_NAME,,}"
  config="$ROOT/dist/$service_name.service"
  sed -i "s/{ USER }/$USER/g" "$config"
  sed -i "s#{ START_COMMAND }#$ROOT/$INTERNAL_NAME.sh service start#g" "$config"
  sudo cp "$config" "$SYSTEMD_CONFIG_DIR"
  sudo systemctl daemon-reload
  sudo systemctl enable "$service_name"
}

# Prevent user from installing poetry as root
if [[ "$EUID" = 0 ]]; then
  log_error "Don't sudo me: './setup.sh'"
  exit 1
fi

parse_args "$@"

check_system_deps
install_project_deps
start_at_boot

log_info "Installation successful, reboot to finish."

exit 0
