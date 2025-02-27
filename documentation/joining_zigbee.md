# Connecting a new device:

- `journalctl -u zigbee2mqtt.service -f`
- Connect according to [instructions](https://www.zigbee2mqtt.io/information/supported_devices.html)
- Get the friendly name from the output
- End the `journalctl` process

Sending test messages:

- `mosquitto_pub -t zigbee2mqtt/<friendly name>/set -m "{\"key\": \"value\"}"`


# Configuring Zigbee:

https://www.zigbee2mqtt.io/guide/installation/01_linux.html#configuring