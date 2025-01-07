from collections import deque
from typing import Any

class Queue:
  '''Queue class that uses collections.deque'''
  
  def __init__(self):
    self.deque = deque()
  
  def pop(self):
    '''Pop the item at the head of the queue'''
    return self.deque.popleft()
  
  def add(self, x: Any):
    '''Add an item to the tail of the queue'''
    self.deque.append(x)
  
  def peek(self):
    '''Peek the item at the head of the queue'''
    return self.deque[0] if self.deque else None
  
  def tail(self):
    '''Peek the item at the tail of the queue'''
    return self.deque[-1] if self.deque else None
  
  def size(self):
    return len(self.deque)
  
  def empty(self) -> bool:    
    return len(self.deque) == 0
  
  def __len__(self):
    return len(self.deque)