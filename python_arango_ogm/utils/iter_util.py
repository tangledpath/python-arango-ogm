from itertools import islice
from typing import List, Iterable, Generator

def chunken(iterable: Iterable, chunk_size: int = 100) -> Generator:
  it = iter(iterable)
  yield from iter(lambda: list(islice(it, chunk_size)), [])

def replace_tuple_item(tpl: tuple, index: int, new_item):
  l = list(tpl)
  l[index] = new_item
  return tuple(l)

# Recursively flatten n-dimensional list into a single list
# Allows for jagged and mixed lists
# TODO: Make recursion a generator?
def flatten(lst: List, flat=[]):
  if (lst):
    for item in lst:
      if isinstance(item, List):
        flatten(item, flat)
      else:
        flat.append(item)
  return flat

  # @staticmethod
  # def chunk_sequence(seq, size):
  #     return (seq[pos:pos + size] for pos in range(0, len(seq), size))
