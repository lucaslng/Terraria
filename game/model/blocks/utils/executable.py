from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Executable(ABC):
  '''Items that have a special effect to be executed when held'''
  @abstractmethod
  def execute(self):
    '''execute whatever needs to be done'''
    pass

  @abstractmethod
  def unexecute(self):
    '''unexecute when item is swapped out'''
    pass