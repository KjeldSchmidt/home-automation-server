from flask import Flask
from flask_apscheduler import APScheduler

_scheduler: APScheduler | None = None


def make_scheduler(app: Flask) -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = APScheduler()
    _scheduler.api_enabled = True
    _scheduler.init_app(app)
    _scheduler.start()


def get_scheduler() -> APScheduler:
    if _scheduler is None:
        raise RuntimeError("Scheduler not initialized - `make_scheduler` must be called once")
    return _scheduler
