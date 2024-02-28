from datetime import datetime
from contextlib import contextmanager
from timeit import default_timer as timer
import sys

SQL_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
EPI_SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

NINETEEN_SEVENTY = datetime(1970, 1, 1)

@contextmanager
def time_and_log(name: str, silent: bool = False):
  """Time and log block (using `with` statement)"""

  if not silent:
    caption = name if name else 'operation'
    print(f"[{caption}] Starting...")
    sys.stdout.flush()
  started_at = timer()
  yield()
  elapsed = timer() - started_at
  if not silent:
    print(f"[{caption}] Processed in in {elapsed:.2f}s.")
    sys.stdout.flush()
  return elapsed
