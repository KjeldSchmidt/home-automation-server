from flask import Flask

import MqttClient
from Controller import Controller


class CeilingLightsCollection(Controller):
    def __init__(
        self,
        lamp_config: dict[str, list[str]],
        app: Flask,
        mqtt_client: MqttClient.Client,
    ):
        self.lights = {}
        for name, lamp_ids in lamp_config.items():
            self.lights[name] = CeilingLights(name, lamp_ids, mqtt_client)

        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route(f"/ceiling/<string:name>/brightness/<int:brightness>")
        def ceiling_lights_brightness(name: str, brightness: int):
            self.lights[name].set_brightness_all(brightness)
            return "Ok", 200

        @app.route(f"/ceiling/<string:name>/temp/<int:color_temp>")
        def ceiling_lights_color(name: str, color_temp: int):
            self.lights[name].set_color_temp_all(color_temp)
            return "Ok", 200

    def produce_main_page_content(self):
        return "<hr />".join(
            [light.produce_main_page_content() for light in self.lights.values()]
        )

    def turn_off_all(self):
        for light in self.lights.values():
            light.set_brightness_all(0)

    def turn_on_all(self):
        for light in self.lights.values():
            light.set_brightness_all(127)


class CeilingLights:
    def __init__(self, name: str, lamp_ids: list[str], mqtt_client: MqttClient.Client):
        self.mqtt_client = mqtt_client
        self.name = name
        self.lamp_ids = lamp_ids

    def produce_main_page_content(self):
        return f"""
            <details>
                <summary>
                    <button onclick="fetch('ceiling/{self.name}/brightness/254')">On</button>
                    <button onclick="fetch('ceiling/{self.name}/brightness/127')">Dim</button>
                    <button onclick="fetch('ceiling/{self.name}/brightness/0')">Off</button>
                </summary> 
                <br /><input type=range min=250 max=454 onchange="fetch(`ceiling/{self.name}/temp/${{this.value}}`)" />
                <br /><input type=range min=0 max=254 onchange="fetch(`ceiling/{self.name}/brightness/${{this.value}}`)" />
            </details>
        """

    def send_to_all_lamps(self, payload):
        for lamp_id in self.lamp_ids:
            self.mqtt_client.publish(
                topic=f"zigbee2mqtt/{lamp_id}/set", payload=payload
            )

    def set_brightness_all(self, brightness: int):
        self.send_to_all_lamps(f'{{ "brightness": "{brightness}" }}')

    def set_color_temp_all(self, color_temp: int):
        self.send_to_all_lamps(f'{{ "color_temp": "{color_temp}" }}')
