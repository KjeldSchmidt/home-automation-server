from paho.mqtt.client import Client as MqttClient

import Scheduler
from Woodlamp import Woodlamp


# Implements https://www.zigbee2mqtt.io/devices/E1603_E1702_E1708.html
class PowerOutlet:
    def __init__(self, woodlamp: Woodlamp, mqtt_client: MqttClient, friendly_name: str):
        self.friendly_name = friendly_name
        self.woodlamp = woodlamp
        self.client: MqttClient = mqtt_client

        Scheduler.scheduler.add_job(
            "Warn about PC turning off",
            lambda: self.woodlamp.set_mode("WarningLights"),
            trigger="cron", hour=0, minute=0, day="*"
        )

        Scheduler.scheduler.add_job(
            "Turn off PC",
            self.turn_off,
            trigger="cron", hour=0, minute=5, day="*"
        )

        Scheduler.scheduler.add_job(
            "Turn off warning lights",
            lambda: self.woodlamp.set_mode("LightsOut"),
            trigger="cron", hour=0, minute=1, day="*"
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