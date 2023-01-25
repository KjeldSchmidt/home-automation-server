#!/usr/bin/env bash

ssh_connect_string=pi@192.168.178.2

## sync: Uploads current code to the rasppi and restart the server service
function task_sync {
  rsync \
    -r . \
    --exclude 'venv' \
    --exclude 'wsl-venv' \
    "${ssh_connect_string}:~/home_automation"
  ssh "${ssh_connect_string}" 'mv home_automation/configuration.yaml /opt/zigbee2mqtt/data/configuration.yaml'

  ssh "${ssh_connect_string}" 'sudo systemctl restart zigbee2mqtt.service'
  ssh "${ssh_connect_string}" 'sudo systemctl restart home-automation.service'
}

## fmt: Apply autoformatting
function task_fmt {
  source wsl-venv/bin/activate
  black .
}

## mypy: Check types
function task_mypy {
  source wsl-venv/bin/activate
  mypy .
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
    pushd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null
    ${resolved_command} "$@"
else
    task_usage
fi