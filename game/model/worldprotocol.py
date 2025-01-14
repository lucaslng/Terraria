from typing import Protocol

class WorldProtocol(Protocol):
	'''Protocol that interfaces World class'''
	def generate(self) -> None:
		...
