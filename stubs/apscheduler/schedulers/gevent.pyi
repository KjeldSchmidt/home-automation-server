from apscheduler.schedulers.base import BaseScheduler as BaseScheduler
from apscheduler.schedulers.blocking import BlockingScheduler as BlockingScheduler

class GeventScheduler(BlockingScheduler):
    def start(self, *args, **kwargs): ...
    def shutdown(self, *args, **kwargs) -> None: ...
