import json
from enum import Enum, auto
from threading import Thread
from typing import Tuple, List

import requests
from flask import Flask, render_template
from flask_apscheduler import APScheduler

import Scheduler
from Controller import Controller
from GlobalState import GlobalState
from TimeFunctions import parse_to_utc, local_time_today


class WoodlampCollection(Controller):
    def __init__(
        self, lamp_config: dict[str, str], app: Flask, global_state: GlobalState
    ):
        self.scheduler: APScheduler = Scheduler.scheduler
        self.next_sundown: str = "No sundown time set"

        self.lights = {}
        for name, lamp_id in lamp_config.items():
            self.lights[name] = Woodlamp(name, lamp_id, global_state)

        self.setup_routes(app)
        self.schedule_scheduling()
        self.schedule_irregular()

    def setup_routes(self, app: Flask):
        @app.route("/woodlamp/<string:name>/mode/<string:mode>")
        def set_mode(name: str, mode: str) -> Tuple[str, int]:
            return self.lights[name].set_mode(mode)

        @app.route("/woodlamp/<string:name>/toggle")
        def toggle_mode(name: str):
            self.lights[name].toggle()
            return "Accepted", 202

    def get_frontend_html(self):
        for light in self.lights.values():
            if not light.available_modes:
                light.fetch_available_modes()

        return render_template(
            "led_strip_lamp.html", next_sundown=self.next_sundown, lights=self.lights
        )

    def turn_off_all(self):
        for light in self.lights.values():
            Thread(target=light.set_mode, args=("LightsOut",)).start()

    def turn_on_all(self):
        for light in self.lights.values():
            Thread(target=light.set_mode, args=("CityAtSundown",)).start()

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


class WoodLampState(Enum):
    CityAtSundown = "CityAtSundown"
    Pacifica = "Pacifica"
    LightsOut = "LightsOut"

    def next(self):
        return {
            WoodLampState.CityAtSundown: WoodLampState.Pacifica,
            WoodLampState.Pacifica: WoodLampState.LightsOut,
            WoodLampState.LightsOut: WoodLampState.CityAtSundown,
        }[self]


class Woodlamp:
    def __init__(self, name: str, lamp_ip: str, global_state: GlobalState):
        self.name = name
        self.lamp_ip = lamp_ip
        self.global_state = global_state
        self.available_modes: List[str] = []

        self.state: WoodLampState = WoodLampState.LightsOut

        self.fetch_available_modes()

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
            if self.global_state.turned_on:
                response = requests.get(f"http://{self.lamp_ip}/setMode?newMode={mode}")
            else:
                return "System is turned off, request is ignored.", 200
            return response.text, response.status_code
        except requests.exceptions.ConnectionError as e:
            print(f"Setting mode on woodlamp {self.name} failed - Error trace:")
            print(e)
            return "Failed", 500

    def toggle(self):
        self.state = self.state.next()
        self.set_mode(self.state.value)
