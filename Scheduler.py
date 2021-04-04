from flask_apscheduler import APScheduler


class Scheduler:
	def __init__( self, app ):
		self.scheduler = APScheduler()
		self.scheduler.api_enabled = True
		self.scheduler.init_app( app )
		self.scheduler.start()
