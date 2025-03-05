import abc
from _typeshed import Incomplete
from apscheduler.triggers.base import BaseTrigger as BaseTrigger
from apscheduler.util import obj_to_ref as obj_to_ref, ref_to_obj as ref_to_obj

class BaseCombiningTrigger(BaseTrigger, metaclass=abc.ABCMeta):
    triggers: Incomplete
    jitter: Incomplete
    def __init__(self, triggers, jitter: Incomplete | None = None) -> None: ...

class AndTrigger(BaseCombiningTrigger):
    def get_next_fire_time(self, previous_fire_time, now): ...

class OrTrigger(BaseCombiningTrigger):
    def get_next_fire_time(self, previous_fire_time, now): ...
