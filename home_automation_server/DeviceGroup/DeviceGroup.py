from flask import Flask

from home_automation_server.Device.Device import Device
from home_automation_server.GuiElement import GuiElement


class DeviceGroup(GuiElement):
    def __init__(self, app: Flask, name: str, devices: list[Device], gui_elements: list[GuiElement]) -> None:
        super().__init__()
        self.devices = devices
        self.gui_elements = gui_elements
        self.name = name

        self._setup_routes(app)

    def _setup_routes(self, app: Flask) -> None:
        @app.route(f"/{self.name}", endpoint=f"device_group_{self.name}")
        def fetch_device_group_frontend() -> str:
            return self.get_frontend_html()

    def get_frontend_html(self) -> str:
        frontend_parts = []
        for device in self.devices:
            frontend_parts.append(device.get_frontend_html())

        for gui_element in self.gui_elements:
            frontend_parts.append(gui_element.get_frontend_html())

        print(frontend_parts)

        return "<br/>".join(frontend_parts)
