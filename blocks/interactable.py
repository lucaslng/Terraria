from abc import ABC


class Interactable(ABC):
  '''Abstract class for something that can be interacted with (press e key when near)'''

  def interact(self):
    '''To be called when Interactable is interacted with.'''
    pass