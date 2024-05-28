from __future__ import annotations

import sys
from contextlib import contextmanager


@contextmanager
def push_argv(argv):
    old_argv = sys.argv
    sys.argv = argv
    yield
    sys.argv = old_argv
