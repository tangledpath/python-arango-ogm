import json
from enum import Enum
from typing import Sequence, Iterable
from math import isnan

def is_int(val):
  return False if safe_int(val) is None else True

def safe_bool(val):
  if not val:
    return False
  if isinstance(val, bool):
    return val
  if isinstance(val, (int, float)):
    return not(not val)
  if isinstance(safe_float(val), float):
    return True if val else False
  return str(val).lower() == 'false'

def safe_float(val, safe_result=None):
  if (val != None):
    try:
      f = float(val)
    except ValueError as x:
      return safe_result
    else:
      return None if isnan(f) else f

def safe_int(val):
  if (val != None):
    try:
      f = float(val)
    except ValueError as x:
      return val
    else:
      return int(f) if not isnan(f) else None

def to_json(obj):
  return json.dumps(obj, indent=1)
