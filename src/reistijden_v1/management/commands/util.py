import contextlib
import time
from itertools import groupby


@contextlib.contextmanager
def profile_it():
    # When pyinstrument is not installed (because we are running in
    # acceptance / production)
    try:
        from pyinstrument import Profiler
    except ImportError:
        yield
    else:
        p = Profiler()
        p.start()
        yield
        p.stop()
        p.print()


@contextlib.contextmanager
def time_it(msg):
    start = time.time()
    yield
    duration = time.time() - start
    print(f'{msg} took {duration} seconds')


def sort_and_group_by(items, key):
    return groupby(sorted(items, key=key), key=key)
