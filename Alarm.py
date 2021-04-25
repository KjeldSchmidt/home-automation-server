from flask import Flask, request

from Scheduler import Scheduler
from TimeFunctions import get_next_valid_time
from Woodlamp import Woodlamp


class Alarm:
	def __init__( self, scheduler: Scheduler, app: Flask, woodlamp: Woodlamp ):
		self.scheduler = scheduler
		self.woodlamp = woodlamp
		self.setup_routes( app )

	@staticmethod
	def produce_main_page_content():
		return '''
			<form class="alarm-form" method="post" action="/alarm">
				<input type="time" name="time" />
				<input type="submit" value="Set Alarm" />
			</form>
		'''

	def wake_up( self ):
		self.woodlamp.set_mode( 'WakeUp' )

	def setup_routes( self, app ):
		@app.route( '/alarm', methods=[ 'POST' ] )
		def set_alarm():
			alarm_time = get_next_valid_time( request.form[ 'time' ] )
			self.scheduler.add_job(
				"Wake up Kjeld",
				self.wake_up,
				next_run_time=alarm_time
			)
			return "OK"
