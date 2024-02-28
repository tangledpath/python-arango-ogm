class frange():
  """
    Floating point range which allows checking presence of an item (inclusive
    of lower; exclusive of upper).  This issn't intended to replace all range
    functions.  However, you can do things like this:
    f_range=frange(3.3, 9.9)
    assert 3.2 not in f_range
    assert 3.3 in f_range
    assert 9.8 in f_range
    assert 9.9 not in f_range
    assert 55 not in f_range
  """

  def __init__(self, lower, upper, upper_inclusive=False):
    if upper < lower:
      raise ValueError(f"Upper should be greater or equal than lower: {upper} < {lower}")
    self.lower = lower
    self.upper = upper
    self.upper_inclusive = upper_inclusive

  def __contains__(self, key):
    k = float(key)
    smaller_upper = (k <= self.upper if self.upper_inclusive else k < self.upper)
    return k >= self.lower and smaller_upper
