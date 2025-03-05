from _typeshed import Incomplete
from apscheduler.schedulers.base import BaseScheduler as BaseScheduler

qtcore: Incomplete
QTimer: Incomplete

class QtScheduler(BaseScheduler):
    def shutdown(self, *args, **kwargs) -> None: ...
    def wakeup(self) -> None: ...
