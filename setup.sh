#!/bin/bash

USER="$(whoami)"
PROJECT="$(basename "$PROJECT_DIR")"

function info() {
  local yel="\\033[1;33m"
  local nc="\\033[0m"

  echo -e "$yel>>$nc $1"
}

function error() {
  local red="\\033[0;31m"
  local nc="\\033[0m"

  echo -e "$red!!$nc $1"
  exit 1
}

# Get the user to install as
# shellcheck disable=SC2039
read -r -p "Install $PROJECT as ? (default:$USER): " u
[ ! -z "$u" ] && USER="$u"

homedir="$(getent passwd "$USER" | cut -d: -f6)"
if [ -z "$homedir" ]; then
  error "User '$USER' does not exist."
  exit 1
fi

# Download project
info "Downloading $PROJECT in $homedir"
git clone "https://github.com/Tastyep/$PROJECT" "$homedir/$PROJECT"

# Install dependencies
info "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y lsof python-pip ||
  error "failed to install dependencies"
pip install --user pipenv ||
  error "failed to install dependencies"

# Configure boot options
info "Adding to startup options (/etc/rc.local)"
# Add to rc.local startup
sudo sed -i /"exit 0"/d /etc/rc.local
printf "~%s/$PROJECT/$PROJECT.sh start\\nexit 0\\n" "$USER" 2>&1 | sudo tee -a /etc/rc.local >/dev/null

# Starting OpenCast
info "Starting $PROJECT"
chmod +x "$homedir/$PROJECT/$PROJECT.sh"
"$homedir/$PROJECT/$PROJECT.sh" start

exit 0
