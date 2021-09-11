from collections import deque
from typing import Iterable


class ToggleList:
	def __init__(self, values : Iterable):
		self.values = deque(values)

	def next( self ):
		next_value = self.values.popleft()
		self.values.append(next_value)
		return next_value
