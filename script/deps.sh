#!/usr/bin/env bash

SHFMT_VERSION="3.1.2"
SC_VERSION="stable"

require_shellcheck() {
  if ! command -v "shellcheck" &>/dev/null; then
    echo -e "Shellcheck not found, installing"
    wget -qO- "https://github.com/koalaman/shellcheck/releases/download/${SC_VERSION?}/shellcheck-${SC_VERSION?}.linux.x86_64.tar.xz" | tar -xJv
    sudo cp "shellcheck-${SC_VERSION}/shellcheck" /usr/local/bin/
    rm -rf "shellcheck-${SC_VERSION}"
    shellcheck --version
  fi
}

require_shfmt() {
  if ! command -v "shfmt" &>/dev/null; then
    local dest="/usr/local/bin/shfmt"
    sudo wget -q "https://github.com/mvdan/sh/releases/download/v${SHFMT_VERSION}/shfmt_v${SHFMT_VERSION}_linux_amd64" -O "$dest"
    sudo chmod +x "$dest"
  fi
}
