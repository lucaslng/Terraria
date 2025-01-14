from abc import ABC, abstractmethod


class Light(ABC):
	'''Abstract base class for lights, lights should set a lightRadius attribute'''

	@property
	@abstractmethod
	def lightRadius(self) -> float:
		'''Radius of the light'''
		pass