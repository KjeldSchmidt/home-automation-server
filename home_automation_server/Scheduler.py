from flask import Flask
from flask_apscheduler import APScheduler

_scheduler = None


def make_scheduler(app: Flask):
    global _scheduler
    _scheduler = APScheduler()
    _scheduler.api_enabled = True
    _scheduler.init_app(app)
    _scheduler.start()


def get_scheduler():
    if _scheduler is None:
        raise RuntimeError("Scheduler not initialized - `make_scheduler` must be called once")
    return _scheduler
