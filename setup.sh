#!/bin/bash

USER="$(whoami)"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$(basename "$PROJECT_DIR")"
INTERNAL_NAME="$(echo "$PROJECT" | cut -f2 -d'-')"
SERVICE_NAME="${INTERNAL_NAME,,}"
SYSTEMD_CONFIG_DIR="/etc/systemd/system/"

# Log an info message.
function info() {
  local yel="\\033[1;33m"
  local nc="\\033[0m"

  echo -e "$yel>>$nc $1"
}

# Log an error message and exit.
function error() {
  local red="\\033[0;31m"
  local nc="\\033[0m"

  echo -e "$red!!$nc $1"
  exit 1
}

# Check if the script is executed from the project or standalone.
# Clone the project and update PROJECT_DIR accordingly is executed in standalone mode.
function setup_environment() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    local homedir

    homedir="$(getent passwd "$USER" | cut -d: -f6)"
    PROJECT_DIR="$homedir/$PROJECT"

    # Download project
    info "Cloning $PROJECT into $PROJECT_DIR"
    git clone "https://github.com/Tastyep/$PROJECT" "$PROJECT_DIR"
  fi
}

# Install system dependencies.
function install_system_deps() {
  info "Installing system dependencies..."

  sudo apt-get update
  sudo apt-get install -y curl lsof python python3 python3-venv python3-pip libdbus-glib-1-dev libdbus-1-dev ||
    error "failed to install dependencies"
  curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" | python3
}

# Install project dependencies.
function install_project_deps() {
  chmod +x "$PROJECT_DIR/$INTERNAL_NAME.sh"
  "$PROJECT_DIR/$INTERNAL_NAME.sh" update
}

# Format and install the systemd config file.
function start_at_boot() {
  info "Setting up startup at boot"

  local config="$PROJECT_DIR/dist/$SERVICE_NAME.service"
  sed -i "s/{ USER }/$USER/g" "$config"
  sed -i "s#{ START_COMMAND }#$PROJECT_DIR/$INTERNAL_NAME.sh start -u#g" "$config"
  sudo cp "$config" "$SYSTEMD_CONFIG_DIR"
  sudo systemctl daemon-reload
  sudo systemctl enable "$SERVICE_NAME"
}

install_system_deps
setup_environment
install_project_deps
start_at_boot

info "Installation successful, reboot to finish."

exit 0
