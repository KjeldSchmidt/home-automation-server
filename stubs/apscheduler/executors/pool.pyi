import abc
from _typeshed import Incomplete
from abc import abstractmethod
from apscheduler.executors.base import BaseExecutor as BaseExecutor, run_job as run_job

class BasePoolExecutor(BaseExecutor, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self, pool): ...
    def shutdown(self, wait: bool = True) -> None: ...

class ThreadPoolExecutor(BasePoolExecutor):
    def __init__(self, max_workers: int = 10, pool_kwargs: Incomplete | None = None) -> None: ...

class ProcessPoolExecutor(BasePoolExecutor):
    pool_kwargs: Incomplete
    def __init__(self, max_workers: int = 10, pool_kwargs: Incomplete | None = None) -> None: ...
