#!/usr/bin/env bash

require_shellcheck() {
  if ! command -v "shellcheck" &>/dev/null; then
    local scversion="stable"
    echo -e "Shellcheck not found, installing"
    wget -qO- "https://github.com/koalaman/shellcheck/releases/download/${scversion?}/shellcheck-${scversion?}.linux.x86_64.tar.xz" | tar -xJv
    sudo cp "shellcheck-${scversion}/shellcheck" /usr/bin/
    rm -rf "shellcheck-${scversion}"
    shellcheck --version
  fi
}

require_go() {
  if ! command -v "go" &>/dev/null; then
    tar -C /usr/local -xzf go1.14.3.linux-amd64.tar.gz
    echo -e "export PATH=\"$PATH:/usr/local/go/bin\"" >> ~/.profile
    source ~/.profile
  fi
}

require_shfmt() {
  if ! command -v "shfmt" &>/dev/null; then
    GO111MODULE=on go get mvdan.cc/sh/v3/cmd/shfmt
  fi
}