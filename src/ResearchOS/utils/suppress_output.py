import sys
import io
import contextlib

@contextlib.contextmanager
def suppress_stdout_stderr():
    new_stdout = io.StringIO()
    new_stderr = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = new_stdout
        sys.stderr = new_stderr
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
