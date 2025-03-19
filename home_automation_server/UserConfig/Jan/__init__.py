from flask import Flask

from MqttHandler import MqttHandler
from .DeviceConfig import DeviceConfig
from Device.ZigbeeLight import ZigbeeLight
from Alarm import Alarm
from .ControllerCollection import ControllerCollection


def initialize(app: Flask, mqtt_handler: MqttHandler) -> ControllerCollection:
    zigbee_lights = {
        name: ZigbeeLight(app, name, lamp_ids, mqtt_handler) for name, lamp_ids in DeviceConfig.zigbee_lights.items()
    }
    alarm = Alarm(app, lambda: zigbee_lights["ceiling-jan"].set_brightness_all(255))

    main_device_group = ControllerCollection(app, "Jan", alarm, zigbee_lights)
    return main_device_group
