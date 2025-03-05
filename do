#!/usr/bin/env bash

ssh_connect_string=pi@192.168.178.2

## sync: Uploads current code to the rasppi and restart the server service
function task_sync {
  rsync \
    -r . \
    --exclude 'venv' \
    --exclude 'wsl-venv' \
    "${ssh_connect_string}:~/home_automation"
  ssh "${ssh_connect_string}" 'mv ~/home_automation/configuration.yaml /opt/zigbee2mqtt/data/configuration.yaml'

  ssh "${ssh_connect_string}" 'sudo systemctl restart zigbee2mqtt.service'
  ssh "${ssh_connect_string}" 'sudo systemctl restart home-automation.service'
}

## fmt: Apply autoformatting
function task_fmt {
  poetry run black .
}

## fmt-check: Checks if formatting is applied correctly
function task_fmt_check {
  poetry run black --check .
}

## mypy: Check types
function task_mypy {
  poetry run mypy home_automation_server
}

## test: runs all local tests
function task_test {
  pushd home_automation_server
  poetry run pytest .
  popd
}

## run: starts the server locally - not for production use
function task_run {
  poetry run python Server.py
}

## setup: Installs the python runtime and dependencies.
function task_setup {
  sudo add-apt-repository ppa:deadsnakes/ppa -y
  sudo apt update
  sudo apt-get install mosquitto python3.10 pipx -y
  pipx install poetry
  pipx ensurepath
  source ~/.bashrc
  poetry install
  git config --local core.hooksPath .githooks/
}

#-------- All task definitions go above this line --------#
function task_usage {
    echo "Usage: $0"
    sed -n 's/^##//p' <"$0" | column -t -s ':' |  sed -E $'s/^/\t/'
}

cmd=${1:-}
shift || true
resolved_command=$(echo "task_${cmd}" | sed 's/-/_/g')
if [[ "$(LC_ALL=C type -t "${resolved_command}")" == "function" ]]; then
    pushd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null || exit
    ${resolved_command} "$@"
else
    task_usage
fi
