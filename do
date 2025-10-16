#!/usr/bin/env bash
set -eu

ssh_connect_string=pi@rpi-home-automation

## sync: Uploads current code to the rasppi and restart the server service
function task_sync {
  poetry export -f requirements.txt --output requirements.txt --without-hashes
  
  rsync \
    -r . \
    --info=progress2 \
    --exclude '.poetry' \
    --exclude 'stubs' \
    "${ssh_connect_string}:~/home-automation-server"
  local user_config_dir
  user_config_dir=$(poetry run python -c "from home_automation_server import env; print(env.USER_CONFIG_MODULE.replace('.', '/'))")

  if ssh "${ssh_connect_string}" "[ -d /opt/zigbee2mqtt/data ]"; then
    ssh "${ssh_connect_string}" "mv ~/home-automation-server/home_automation_server/${user_config_dir}/configuration.yaml /opt/zigbee2mqtt/data/configuration.yaml"
    ssh "${ssh_connect_string}" 'sudo systemctl restart zigbee2mqtt.service'
  fi

  if ssh "${ssh_connect_string}" "systemctl list-unit-files | grep -q home-automation-server.service"; then
    ssh "${ssh_connect_string}" 'sudo systemctl restart home-automation-server.service'
  fi
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

## setup: Installs the python runtime and dependencies for local development
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

##pi-status: check the status of all three systemctl services
function task_pi_status {
  printf "Checking status of systemctl services...\n\n"
  
  if [[ "$USER" == "pi" ]]; then
    # Running directly on Raspberry Pi
    printf "Running locally on Raspberry Pi\n\n"
    _pi_status_local
  else
    # Running from remote machine, SSH to Pi
    printf "Running via SSH to Raspberry Pi\n\n"
    ssh "${ssh_connect_string}" "$(declare -f _pi_status_local); _pi_status_local"
  fi
}

function _pi_status_local {
  echo "=== MOSQUITTO SERVICE ==="
  sudo systemctl status mosquitto.service --no-pager -l || true
  echo ""
  
  echo "=== ZIGBEE2MQTT SERVICE ==="
  sudo systemctl status zigbee2mqtt.service --no-pager -l || true
  echo ""
  
  echo "=== HOME-AUTOMATION-SERVER SERVICE ==="
  sudo systemctl status home-automation-server.service --no-pager -l || true
  echo ""
  
  echo "=== SUMMARY ==="
  echo "Active services:"
  sudo systemctl is-active mosquitto.service zigbee2mqtt.service home-automation-server.service || true
  echo ""
  echo "Enabled services:"
  sudo systemctl is-enabled mosquitto.service zigbee2mqtt.service home-automation-server.service || true
}

##pi-setup: prepare a fresh raspberry pi OS installation to run the required software
function task_pi_setup {
  _pi_install_mosquitto
  printf "Mosquitto is probably maybe installed ✅\n"
  printf "Starting mosquitto service...\n\n"
  sudo systemctl enable mosquitto.service

  _pi_install_zigbee2mqtt
  printf "Zigbee2Mqtt is probably maybe installed ✅\n"
  printf "Starting zigbee2mqtt service...\n\n"
  sudo systemctl enable zigbee2mqtt.service

  _pi_install_python_deps
  printf "Python dependencies are probably maybe installed ✅\n"
  printf "Starting home-automation-server service...\n\n"
  sudo systemctl enable home-automation-server.service
}

function _pi_install_mosquitto {
  sudo apt install -y mosquitto mosquitto-clients
}

function _pi_install_python_deps {
  sudo apt update
  sudo apt-get install -y python3-pip python3-venv python3-lxml

  python3 -m venv --system-site-packages ~/home-automation-server/venv
  source ~/home-automation-server/venv/bin/activate
  pip install --upgrade pip
  
  # Create a temporary requirements file without lxml
  grep -v "^lxml" ~/home-automation-server/requirements.txt > /tmp/requirements_no_lxml.txt
  
  # Install requirements without lxml
  pip install -r /tmp/requirements_no_lxml.txt

  sudo mv documentation/home-automation-server.service /etc/systemd/system/home-automation-server.service
}

function _pi_install_zigbee2mqtt {
  sudo mv documentation/zigbee2mqtt.service /etc/systemd/system/zigbee2mqtt.service

  if [ -f /opt/zigbee2mqtt/.installation-complete ]; then
    echo "Zigbee2MQTT already installed, skipping..."
    echo "If you want to reinstall Zigbee2MQTT, run"
    echo "sudo rm /opt/zigbee2mqtt/.installation-complete"
    echo "And then rerun the command"
    return
  fi


  sudo rm -rf /opt/zigbee2mqtt
  sudo mkdir -p /opt/zigbee2mqtt

  pushd /opt/zigbee2mqtt

  sudo apt-get install -y curl
  sudo curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt-get install -y nodejs git make g++ gcc libsystemd-dev
  sudo corepack enable

  sudo chown -R ${USER}: /opt/zigbee2mqtt

  git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt

  echo "Y" | pnpm install --frozen-lockfile
  touch .installation-complete

  popd
}

#-------- All task definitions go above this line --------#
# Bash Strict Mode - For details, see
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -u     # Raise error when using undefined variables
set -e     # Raise error if any command has a non-zero exit status
# set -x   # Enable this optionally to print every command executed by bash
set -o pipefail  # Prevent pipelines from masking errors

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
