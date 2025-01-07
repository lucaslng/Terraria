from collections import deque
from typing import Any

class Queue:
  '''Queue class that uses collections.deque'''
  
  def __init__(self):
    self._deque = deque()
  
  def pop(self):
    '''Pop the item at the head of the queue'''
    return self._deque.popleft()
  
  def add(self, x: Any):
    '''Add an item to the tail of the queue'''
    self._deque.append(x)
  
  def peek(self):
    '''Peek the item at the head of the queue'''
    return self._deque[0] if self._deque else None
  
  def tail(self):
    '''Peek the item at the tail of the queue'''
    return self._deque[-1] if self._deque else None
  
  def size(self):
    '''Returns the length of the queue'''
    return len(self._deque)
  
  def __len__(self):
    return len(self._deque)
  
  def __repr__(self):
    return repr(self._deque)