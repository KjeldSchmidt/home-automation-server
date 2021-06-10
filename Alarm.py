from typing import Dict
from uuid import uuid1

from apscheduler.job import Job
from flask import Flask, request, redirect
from flask_apscheduler import APScheduler

from TimeFunctions import get_next_valid_time, local_time_today
from Woodlamp import Woodlamp


class Alarm:
	def __init__( self, scheduler: APScheduler, app: Flask, woodlamp: Woodlamp ):
		self.scheduler: APScheduler = scheduler
		self.woodlamp = woodlamp
		self.setup_routes( app )
		self.alarms: Dict[ str, Job ] = { }

	def produce_main_page_content( self ):
		alarm_elements = [ self.make_alarm_component( job_id, alarm ) for job_id, alarm in self.alarms.items() ]
		set_alarms = '<br />'.join( alarm_elements )
		return f'''
			<form class="alarm-form" method="post" action="/alarm">
				<input type="time" name="time" />
				<input type="submit" value="Set Alarm" />
				<br />
				{set_alarms}
			</form>
		'''

	@staticmethod
	def make_alarm_component( job_id: str, job: Job ):
		return f"""
		{local_time_today( job.next_run_time )} <a href="/alarm/{job_id}/delete"> X </a> 
		"""

	def wake_up( self ):
		self.woodlamp.set_mode( 'WakeUp' )

	def setup_routes( self, app ):
		@app.route( '/alarm', methods=[ 'POST' ] )
		def set_alarm():
			alarm_time = get_next_valid_time( request.form[ 'time' ] )
			job_id = f"alarm {uuid1()}"
			new_alarm = self.scheduler.add_job(
				job_id,
				self.wake_up,
				next_run_time=alarm_time
			)
			self.alarms[ job_id ] = new_alarm
			return redirect( "/" )

		@app.route( '/alarm/<string:job_id>/delete' )
		def delete_mode( job_id: str ):
			self.scheduler.remove_job( job_id )
			self.alarms.pop( job_id )
			return redirect( "/" )
