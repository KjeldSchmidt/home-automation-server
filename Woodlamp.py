import json
from threading import Thread
from typing import Tuple, List

import requests
from flask import Flask
from flask_apscheduler import APScheduler

import Scheduler
from Controller import Controller
from TimeFunctions import parse_to_utc, local_time_today


class WoodlampCollection:
    def __init__(
            self,
            lamp_config: dict[str, str],
            app: Flask,
    ):
        self.scheduler: APScheduler = Scheduler.scheduler
        self.next_sundown: str = "No sundown time set"

        self.lights = {}
        for name, lamp_id in lamp_config.items():
            self.lights[name] = Woodlamp(name, lamp_id)

        self.setup_routes(app)
        self.schedule_scheduling()
        self.schedule_irregular()

    def setup_routes(self, app: Flask):
        @app.route("/woodlamp/<string:name>/mode/<string:mode>")
        def set_mode(name: str, mode: str):
            return self.lights[name].set_mode(mode)

    def produce_main_page_content(self):
        return f"""
            Next sundown at: {self.next_sundown} 
            </br>
            {"<hr />".join([light.produce_main_page_content() for light in self.lights.values()])}
        """

    def turn_off_all(self):
        for light in self.lights.values():
            Thread(target=light.set_mode, args=("LightsOut", )).start()

    def turn_on_all(self):
        for light in self.lights.values():
            Thread(target=light.set_mode, args=("CityAtSundown", )).start()

    def schedule_sundown_lamp(self) -> None:
        try:
            sun_times_json = requests.get(
                "https://api.sunrise-sunset.org/json?lat=51&lng=7&formatted=0"
            )
        except Exception as e:
            print(f"Error: Failure when fetching sunrise times. Error message: {e}")
            return
        sun_times_times_utc = json.loads(sun_times_json.text)["results"]
        twilight_start_string = sun_times_times_utc["sunset"][:-6]
        twilight_start_utc = parse_to_utc(twilight_start_string, "%Y-%m-%dT%H:%M:%S")

        self.next_sundown = local_time_today(twilight_start_utc)
        self.scheduler.add_job(
            "Turn on city lights",
            self.turn_on_all,
            next_run_time=twilight_start_utc,
        )

    def schedule_scheduling(self) -> None:
        self.scheduler.add_job(
            "Schedule Wood Lamp Controller",
            self.schedule_irregular,
            trigger="cron",
            hour=3,
            day="*",
        )

    def schedule_irregular(self) -> None:
        self.schedule_sundown_lamp()


class Woodlamp(Controller):
    def __init__(self, name: str, lamp_ip: str):
        self.name = name
        self.lamp_ip = lamp_ip
        self.available_modes: List[str] = []

        self.current_mode: str | None = None
        self.fetch_available_modes()

    def produce_main_page_content(self):
        def make_link(mode):
            return f"<button onclick=\"fetch('/woodlamp/{self.name}/mode/{mode}')\">{mode}</button>"

        if not self.available_modes:
            self.fetch_available_modes()

        mode_links = [make_link(mode) for mode in self.available_modes]
        modes_block = f'<div class="modes_block"> {"".join(mode_links)} </div>'
        color_wheel_block = self.make_color_wheel_block()

        return f"""
        Set color mode:	{modes_block} </br>
        {color_wheel_block}
        """

    def make_color_wheel_block(self):
        return f"""
        <div id="picker"></div>
        <script src="https://cdn.jsdelivr.net/npm/@jaames/iro@5"></script>
        <script type="text/javascript">
            var colorPicker = new iro.ColorPicker('#picker', {{ layoutDirection: "horizontal" }});
    
            colorPicker.on('color:change', color => {{
                const colorString = "0x" + color.hexString.substring(1);
                fetch( "/woodlamp/{self.name}/mode/SingleColor&color=" + colorString );
            }});
        </script>
        """

    def fetch_available_modes(self) -> None:
        try:
            response = requests.get(f"http://{self.lamp_ip}/getModes")
        except requests.exceptions.ConnectionError:
            return

        mode_names = response.text.split(",")
        mode_names = [mode.strip() for mode in mode_names]
        self.available_modes = mode_names

    def set_mode(self, mode: str) -> Tuple[str, int]:
        self.current_mode = mode
        try:
            response = requests.get(f"http://{self.lamp_ip}/setMode?newMode={mode}")
            return response.text, response.status_code
        except requests.exceptions.ConnectionError as e:
            print(f"Setting mode on woodlamp {self.name} failed - Error trace:")
            print(e)
            return "Failed", 500
