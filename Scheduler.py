from flask import Flask
from flask_apscheduler import APScheduler

scheduler = None


def make_scheduler(app: Flask):
    global scheduler
    scheduler = APScheduler()
    scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()
