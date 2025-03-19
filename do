#!/usr/bin/env bash
set -eu

ssh_connect_string=pi@192.168.178.2

## sync: Uploads current code to the rasppi and restart the server service
function task_sync {
  rsync \
    -r . \
    --exclude 'venv' \
    --exclude 'wsl-venv' \
    "${ssh_connect_string}:~/home-automation-server"
  local user_config_dir
  user_config_dir=$(poetry run python -c "from home_automation_server import env; print(env.USER_CONFIG_MODULE.replace('.', '/'))")
  ssh "${ssh_connect_string}" "mv ~/home-automation-server/home_automation_server/${user_config_dir}/configuration.yaml /opt/zigbee2mqtt/data/configuration.yaml"

  ssh "${ssh_connect_string}" 'sudo systemctl restart zigbee2mqtt.service'
  ssh "${ssh_connect_string}" 'sudo systemctl restart home-automation-server.service'
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
  pushd home_automation_server
  poetry run mypy .
  popd
}

## test: runs all local tests
function task_test {
  pushd home_automation_server
  poetry run pytest .
  popd
}

## run: starts the server locally - not for production use
function task_run {
  poetry run python home_automation_server/main.py
}

## quality-gates: runs local quality gates, e.g. before commiting
function task_quality_gates {
  task_fmt
  task_mypy
  task_test
}

## setup: Installs the python runtime and dependencies.
function task_setup { #todo: separate setup for prod&local
  sudo add-apt-repository ppa:deadsnakes/ppa -y #this needs to go only in local
  sudo apt update
  sudo apt-get install mosquitto python3.10 pipx -y
  pipx install poetry
  pipx ensurepath
  source ~/.bashrc
  poetry install
  git config --local core.hooksPath .githooks/ #this needs to go only in local
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
