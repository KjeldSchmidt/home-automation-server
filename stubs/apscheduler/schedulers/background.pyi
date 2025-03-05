from apscheduler.schedulers.base import BaseScheduler as BaseScheduler
from apscheduler.schedulers.blocking import BlockingScheduler as BlockingScheduler
from apscheduler.util import asbool as asbool

class BackgroundScheduler(BlockingScheduler):
    def start(self, *args, **kwargs) -> None: ...
    def shutdown(self, *args, **kwargs) -> None: ...
