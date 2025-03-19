from typing_extensions import Self

from flask import Flask, render_template

from Device.Device import Device
from Alarm import Alarm
from Device.ZigbeeLight import ZigbeeLight
from DeviceGroup.DeviceGroup import DeviceGroup


class ControllerCollection(DeviceGroup):
    def __init__(
        self,
        app: Flask,
        name: str,
        alarm: Alarm,
        zigbee_lights: dict[str, ZigbeeLight],
    ):
        self.controllers: list[Device] = [
            *zigbee_lights.values(),
        ]

        self.gui_elements = [
            alarm,
            *zigbee_lights.values(),
        ]

        super().__init__(app, name, self.controllers, self.gui_elements)
        self.alarm = alarm
        self.zigbee_lights = zigbee_lights

    def turn_off_all(self: Self) -> None:
        for controller in self.controllers:
            controller.turn_off_all()

    def turn_on_all(self: Self) -> None:
        for controller in self.controllers:
            controller.turn_on_all()

    def get_frontend_html(self: Self) -> str:
        return render_template("index.html", gui_elements=self.gui_elements)
