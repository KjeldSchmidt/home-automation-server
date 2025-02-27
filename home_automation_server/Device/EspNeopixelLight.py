import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Tuple, List

import requests
from flask import Flask, render_template
from flask_apscheduler import APScheduler

import Scheduler
from Device.Device import Device
from Device.GlobalState import GlobalState
from TimeFunctions import parse_to_utc, local_time_today


class EspNeopixelLightState(Enum):
    CityAtSundown = "CityAtSundown"
    Pacifica = "Pacifica"
    LightsOut = "LightsOut"

    def next(self):
        return {
            EspNeopixelLightState.CityAtSundown: EspNeopixelLightState.Pacifica,
            EspNeopixelLightState.Pacifica: EspNeopixelLightState.LightsOut,
            EspNeopixelLightState.LightsOut: EspNeopixelLightState.CityAtSundown,
        }[self]


class EspNeopixelLight(Device):
    def __init__(self, app: Flask, name: str, lamp_ip: str, global_state: GlobalState):
        self.name = name
        self.lamp_ip = lamp_ip
        self.global_state = global_state
        self.available_modes: List[str] = []

        self.state: EspNeopixelLightState = EspNeopixelLightState.LightsOut

        self.scheduler: APScheduler = Scheduler.scheduler
        self.next_sundown: datetime | None = None

        self.schedule_scheduling()
        self.schedule_irregular()

        self.fetch_available_modes()
        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route(f"/esp_neopixel_light/{self.name}/mode/<string:mode>", endpoint=f"mode_{self.name}")
        def set_mode(mode: str) -> Tuple[str, int]:
            return self.set_mode(mode)

        @app.route(f"/esp_neopixel_light/{self.name}/toggle", endpoint=f"toggle_{self.name}")
        def toggle_mode():
            self.toggle()
            return "Accepted", 202

    def fetch_available_modes(self) -> None:
        try:
            response = requests.get(f"http://{self.lamp_ip}/getModes")
        except requests.exceptions.ConnectionError:
            return

        mode_names = response.text.split(",")
        mode_names = [mode.strip() for mode in mode_names]
        self.available_modes = mode_names

    def set_mode(self, mode: str) -> Tuple[str, int]:
        try:
            if self.global_state.is_turned_on:
                response = requests.get(f"http://{self.lamp_ip}/setMode?newMode={mode}")
            else:
                return "System is turned off, request is ignored.", 200
            return response.text, response.status_code
        except requests.exceptions.ConnectionError as e:
            print(f"Setting mode on esp_neopixel_light {self.name} failed - Error trace:")
            print(e)
            return "Failed", 500

    def toggle(self):
        self.state = self.state.next()
        self.set_mode(self.state.value)

    def get_frontend_html(self):
        if not self.available_modes:
            self.fetch_available_modes()

        return render_template(
            "led_strip_lamp.html", next_sundown=self.next_sundown, light=self
        )

    def turn_off_all(self):
        self.set_mode("LightsOut")

    def turn_on_all(self):
        self.set_mode("CityAtSundown")

    def schedule_sundown_lamp(self) -> None:
        self.scheduler.add_job(
            f"Turn on city lights for {self.name}",
            self.turn_on_all,
            next_run_time=self.get_next_sundown_time(),
        )

    def get_next_sundown_time(self) -> datetime:
        try:
            sun_times_json = requests.get(
                "https://api.sunrise-sunset.org/json?lat=51&lng=7&formatted=0"
            )
        except Exception as e:
            print(f"Error: Failure when fetching sunrise times - reusing last known time. Error message: {e}")
            return self.next_sundown + timedelta(days=1)

        sun_times_times_utc = json.loads(sun_times_json.text)["results"]
        twilight_start_string = sun_times_times_utc["sunset"][:-6]
        twilight_start_utc = parse_to_utc(twilight_start_string, "%Y-%m-%dT%H:%M:%S")

        self.next_sundown = twilight_start_utc
        return twilight_start_utc

    def get_local_next_sundown(self) -> str:
        return local_time_today(self.next_sundown)

    def schedule_scheduling(self) -> None:
        """
        Every day, we fetch the sunset time for that day and
        schedule turning them on at that time.

        :return: None
        """
        self.scheduler.add_job(
            f"Schedule next Sundown for {self.name}",
            self.schedule_irregular,
            trigger="cron",
            hour=3,
            day="*",
        )

    def schedule_irregular(self) -> None:
        self.schedule_sundown_lamp()