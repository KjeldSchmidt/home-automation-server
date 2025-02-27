from uuid import uuid1

from apscheduler.job import Job
from flask import Flask, request, redirect
from flask_apscheduler import APScheduler

import Scheduler
from Device.EspNeopixelLight import EspNeopixelLight
from TimeFunctions import get_next_valid_time, local_time_today


class Alarm:
    def __init__(self, app: Flask, esp_neopixel_light: EspNeopixelLight):
        self.scheduler: APScheduler = Scheduler.scheduler
        self.esp_neopixel_light = esp_neopixel_light
        self.setup_routes(app)

    def get_frontend_html(self):
        alarms = [job for job in self.scheduler.get_jobs() if job.id.startswith("alarm::")]
        alarm_elements = [self.make_alarm_component(alarm) for alarm in alarms]
        set_alarms = "<br />".join(alarm_elements)
        return f"""
            <form class="alarm-form" method="post" action="/alarm">
                <input type="time" name="time" />
                <input type="submit" value="Set Alarm" />
                <br />
                {set_alarms}
            </form>
        """

    @staticmethod
    def make_alarm_component(job: Job):
        return f"""{local_time_today( job.next_run_time )} <a href="/alarm/{job.id}/delete"> X </a>"""

    def wake_up(self):
        self.esp_neopixel_light.set_mode("WakeUp")

    def setup_routes(self, app):
        @app.route("/alarm", methods=["POST"])
        def set_alarm():
            alarm_time = get_next_valid_time(request.form["time"])
            job_id = f"alarm::{uuid1()}"
            self.scheduler.add_job(job_id, self.wake_up, next_run_time=alarm_time)
            return redirect("/")

        @app.route("/alarm/<string:job_id>/delete")
        def delete_mode(job_id: str):
            self.scheduler.remove_job(job_id)
            return redirect("/")
