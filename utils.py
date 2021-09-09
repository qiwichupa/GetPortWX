import sys
from contextlib import contextmanager
from io import StringIO

# stdout redirect:
#   out = StringIO()
#   with captureStdOut(out):
#       some_func_with_prints()
#   out.getvalue()
@contextmanager
def captureStdOut(output):

    stdout = sys.stdout
    sys.stdout = output
    try:
        yield
    finally:
        sys.stdout = stdout