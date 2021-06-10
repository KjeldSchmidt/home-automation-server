from flask import Flask
from flask_apscheduler import APScheduler


def make_scheduler( app: Flask ):
	scheduler = APScheduler()
	scheduler.api_enabled = True
	scheduler.init_app( app )
	scheduler.start()
	return scheduler
