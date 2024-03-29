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
SYSTEMD_CONFIG_DIR=".config/systemd/user"
TEMPLATE_DIR="$ROOT/template"
DOWNLOAD_DIRECTORY="$ROOT/library"

# shellcheck source=script/cli_builder.sh
source "$ROOT/script/cli_builder.sh"
# shellcheck source=script/logging.sh
source "$ROOT/script/logging.sh"

# Install system dependencies.
check_system_deps() {
  log_info "Checking system dependencies..."
  local -a deps=("curl" "lsof" "python" "python3" "pip3" "npm" "node")
  local status fail
  # Set flags to false  by default
  [[ -z "${ARGS["--ci"]}" ]] && deps+=("ffmpeg" "vlc")

  fail=false
  for dep in "${deps[@]}"; do
    command -v "$dep" &>/dev/null
    status="$?"
    log_status "$dep" "$status"

    if [[ "$status" != "0" ]]; then
      case "$dep" in
      "npm" | "node")
        install_nvm
        status="$?"
        ;;
      esac
    fi
    [[ "$status" != "0" ]] && fail=true
  done

  if [[ "$fail" = true ]]; then
    log_error "Missing dependencies, please install them."
    exit 1
  fi
}

# Install node version manager (nvm)
# Install node and npm using nvm
install_nvm() {
  log_info "Installing nvm..."
  curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.0/install.sh" | PROFILE=~/.profile bash
  # shellcheck source=/dev/null
  source ~/.profile
  # Install npm as well
  nvm install node
}

# Install project dependencies.
install_project_deps() {
  log_info "Installing project dependencies..."

  curl -sSL https://install.python-poetry.org | python3 -
  "$ROOT/$INTERNAL_NAME.sh" deps install
}

build_service() {
  log_info "Creating a production build of the webapp..."

  "$ROOT/$INTERNAL_NAME.sh" build webapp
}

# Configure the service
config_service() {
  log_info "Configuring $INTERNAL_NAME"

  mkdir -p "$DOWNLOAD_DIRECTORY"
  sed "s#{ OUTPUT_DIRECTORY }#$DOWNLOAD_DIRECTORY#g" "$TEMPLATE_DIR/config.yml" |
    tee "$ROOT/config.yml" >/dev/null
  log_info "Download directory configured as '$DOWNLOAD_DIRECTORY'"
}

# Format and install the systemd config file.
start_at_boot() {
  log_info "Setting up $INTERNAL_NAME service"

  local service_name config
  # lowercase
  service_name="${INTERNAL_NAME,,}"
  config="$TEMPLATE_DIR/$service_name.service"
  mkdir -p "$HOME/$SYSTEMD_CONFIG_DIR"
  sed "s#{ START_COMMAND }#$ROOT/$INTERNAL_NAME.sh service start#g
       s#{ STOP_COMMAND }#$ROOT/$INTERNAL_NAME.sh service stop#g" -- "$config" |
    tee "$HOME/$SYSTEMD_CONFIG_DIR/$service_name.service" >/dev/null
  systemctl --user daemon-reload
  systemctl --user enable "$service_name"
}

# Prevent user from installing poetry as root
if [[ "$EUID" = 0 ]]; then
  log_error "Don't sudo me: './setup.sh'"
  exit 1
fi

parse_args "$@"

check_system_deps
install_project_deps
build_service
config_service
start_at_boot

log_info "Installation successful, reboot to finish."

exit 0
