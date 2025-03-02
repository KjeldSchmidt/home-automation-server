from flask import Flask

from Device.Device import Device
from GuiElement import GuiElement


class DeviceGroup(GuiElement):
    def __init__(self, app: Flask, name: str, devices: list[Device]) -> None:
        super().__init__()
        self.devices = devices
        self.name = name

        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route(f"/{self.name}", endpoint=f"device_group_{self.name}")
        def fetch_device_group_frontend() -> str:
            return self.get_frontend_html()

    def get_frontend_html(self) -> str:
        frontend_parts = []
        for device in self.devices:
            frontend_parts.append(device.get_frontend_html())

        return "<br/>".join(frontend_parts)
