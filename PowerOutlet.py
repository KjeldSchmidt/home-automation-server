from paho.mqtt.client import Client as MqttClient

import Scheduler


# Implements https://www.zigbee2mqtt.io/devices/E1603_E1702_E1708.html
class PowerOutlet:
    def __init__(self, mqtt_client: MqttClient, friendly_name: str):
        self.friendly_name = friendly_name
        self.client: MqttClient = mqtt_client

        Scheduler.scheduler.add_job(
            "Warn about PC turning off",
            self.turn_off,
            trigger="cron", hour=1, minute=5, day="*"
        )

        Scheduler.scheduler.add_job(
            "Turn off PC",
            self.turn_off,
            trigger="cron", hour=1, minute=5, day="*"
        )

        Scheduler.scheduler.add_job(
            "Re-enable PC",
            self.turn_on,
            trigger="cron", hour=2, day="*"
        )

    def turn_on(self):
        self.client.publish(
            topic=f"zigbee2mqtt/{self.friendly_name}/set",
            payload='{"state": "on"}'
        )

    def turn_off(self):
        self.client.publish(
            topic=f"zigbee2mqtt/{self.friendly_name}/set",
            payload='{"state": "off"}'
        )