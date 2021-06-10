from typing import List
from uuid import uuid1

from apscheduler.job import Job
from flask import Flask, request

from Scheduler import Scheduler
from TimeFunctions import get_next_valid_time, local_time_today
from Woodlamp import Woodlamp


class Alarm:
	def __init__( self, scheduler: Scheduler, app: Flask, woodlamp: Woodlamp ):
		self.scheduler = scheduler
		self.woodlamp = woodlamp
		self.setup_routes( app )
		self.alarms: List[ Job ] = [ ]

	def produce_main_page_content( self ):
		alarm_elements = [ local_time_today( alarm.next_run_time ) for alarm in self.alarms ]
		set_alarms = '<br />'.join( alarm_elements )
		return f'''
			<form class="alarm-form" method="post" action="/alarm">
				<input type="time" name="time" />
				<input type="submit" value="Set Alarm" />
				<br />
				{set_alarms}
			</form>
		'''

	def wake_up( self ):
		self.woodlamp.set_mode( 'WakeUp' )

	def setup_routes( self, app ):
		@app.route( '/alarm', methods=[ 'POST' ] )
		def set_alarm():
			alarm_time = get_next_valid_time( request.form[ 'time' ] )
			new_alarm = self.scheduler.add_job(
				f"alarm {uuid1()}",
				self.wake_up,
				next_run_time=alarm_time
			)
			self.alarms.append( new_alarm )
			return "OK"
