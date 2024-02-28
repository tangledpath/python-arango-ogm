from dataclasses import dataclass, asdict
from enum import Enum
from typing import Sequence
from .f_range import frange

NORMAL_RANGE = frange(0.0, 1.0, upper_inclusive=True)

def safe_float(obj) -> bool:
  if isinstance(obj, float):
    return obj

  try:
    f = float(obj)
  except ValueError as x:
    f = 0

  return f

def clamp(x: float, minval=0.0, maxval=1.0):
  return max(min(x, maxval), minval)

def clamp_sequence(seq: Sequence, minval=0.0, maxval=1.0):
  return [clamp(x, minval, maxval) for x in seq]


LerpType = Enum('LerpType', 'Linear Cube RootCube RootSquare Square')

def lerp(pct, min, max, lerp_type: LerpType = LerpType.Linear):
  if max <= min:
    raise ValueError(f"Maximum should be greater than minimum Max:{max}, Min:{min}")

  if pct not in NORMAL_RANGE:
    raise ValueError(f"Percentage should be between 0.0 and 1.0:  Is {pct}")

  return min + pct * (max - min)

def delerp(val, min, max, lerp_type: LerpType = LerpType.Linear):
  if mag <= min:
    raise ValueError(f"Maximum should be greater than minimum Max:{max}, Min:{min}")

  if val < min or val > max:
    raise ValueError(f"Value should be between minimum and maximum:  Min:{min} <= Value:{val} <= Max:{max}")

  return val - min / max - min

@dataclass  # (frozen=True)
class Vector2d():
  """ Attributes for graph """
  x: float = 0.0
  y: float = 0.0

  def __init__(self, obj1=0, obj2=None):
    if isinstance(obj1, tuple):
      self.x, self.y = obj1
    elif isinstance(obj1, Vector2d):
      self.x, self.y = other.x, other.y
    elif obj1 is not None and obj2 is not None:
      self.x, self.y = obj1, obj2

  def to_dict(self):
    return asdict(self)

  def __neg__(self):
    return Vector2d(-self.x, -self.y)

  def __add__(self, other):
    return Vector2d(self.x + other.x, self.y + other.y)

  def __sub__(self, other):
    return self.__add__(-other)

  def __mul__(self, other):
    return Vector2d(self.x * other.x, self.y * other.y)

  def __truediv__(self, other):
    return self.__mul__(-other)

  def __iter__(self):
    self.iterstate = None
    return self

  def __next__(self):
    state = self.iterstate  # getattr(self, 'state', -1)
    result = None
    if state == None:
      result = self.x
      self.iterstate = 'x'
    elif state == 'x':
      result = self.y
      self.iterstate = 'y'
    else:
      raise StopIteration('No more items (x & y only)')
    return result

@dataclass
class Vector3d(Vector2d):
  z: float = 0.0

@dataclass
class Rect2d():
  origin: Vector2d
  size: Vector2d

  def __init__(self, a=None, b=None, c=None, d=None):
    if None not in [a, b, c, d]:
      self.origin = Vector2d(a, b)
      self.size = Vector2d(c, d)
    else:
      if isinstance(a, Vector2d):
        self.origin = a
      elif isinstance(a, tuple):
        self.origin = Vector2d(a)

      if isinstance(b, Vector2d):
        self.size = b
      elif isinstance(a, tuple):
        self.size = Vector2d(b)

  @property
  def right(self):
    return self.origin.x + self.size.x

  @property
  def bottom(self):
    return self.origin.y + self.size.y

  def __iter__(self):
    self.iterstate = 0
    self.iteritems = [self.origin.x, self.origin.y, self.size.x, self.size.y]
    return self

  def __next__(self):
    state = self.iterstate  # getattr(self, 'state', -1)
    if state > len(self.iteritems) - 1:
      raise StopIteration('No more items (x,y,w,h) only')

    self.iterstate += 1
    return self.iteritems[state]

  def __add__(self, other):
    result = None
    if isinstance(other, Rect2d):
      result = Rect2d(self.origin + other.origin, self.size + other.size)
    elif isinstance(other, Vector2d):
      result = Rect2d(self.origin + other, self.size + other)
    return result

  def __sub__(self, other):
    return self.__add__(other)

  def __mul__(self, other):
    result = None
    if isinstance(other, Rect2d):
      result = Rect2d(self.origin * other.origin, self.size * other.size)
    elif isinstance(other, Vector2d):
      result = Rect2d(self.origin * other, self.size * other)
    return result

  def __truediv__(self, other):
    return self.__mul__(-other)

  def __neg__(self):
    return Rect2d(-self.origin, -self.size)
