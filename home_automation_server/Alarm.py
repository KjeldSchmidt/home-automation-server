from uuid import uuid1

from flask import Flask, request, redirect, render_template
from werkzeug.wrappers import Response
from flask_apscheduler import APScheduler

from home_automation_server import Scheduler
from home_automation_server.Device.EspNeopixelLight import EspNeopixelLight
from home_automation_server.GuiElement import GuiElement
from home_automation_server.util.TimeFunctions import get_next_valid_time, local_time_today


class Alarm(GuiElement):
    def __init__(self, app: Flask, esp_neopixel_light: EspNeopixelLight) -> None:
        self.scheduler: APScheduler = Scheduler.get_scheduler()
        self.esp_neopixel_light = esp_neopixel_light
        self._setup_routes(app)

    def get_frontend_html(self) -> str:
        active_alarms = [job for job in self.scheduler.get_jobs() if job.id.startswith("alarm::")]
        return render_template("alarm.html", active_alarms=active_alarms, local_time_today=local_time_today)

    def wake_up(self) -> None:
        self.esp_neopixel_light.set_mode("WakeUp")

    def _setup_routes(self, app: Flask) -> None:
        @app.route("/alarm", methods=["POST"])
        def set_alarm() -> Response:
            alarm_time = get_next_valid_time(request.form["time"])
            job_id = f"alarm::{uuid1()}"
            self.scheduler.add_job(job_id, self.wake_up, next_run_time=alarm_time)
            return redirect("/")

        @app.route("/alarm/<string:job_id>/delete")
        def delete_mode(job_id: str) -> Response:
            self.scheduler.remove_job(job_id)
            return redirect("/")
