from python_arango_ogm.utils.f_range import frange

def test_frange():
  f_range = frange(3.3, 9.9)
  assert 3.2 not in f_range
  assert 3.3 in f_range
  assert 9.8 in f_range
  assert 9.9 not in f_range
  assert 55 not in f_range
