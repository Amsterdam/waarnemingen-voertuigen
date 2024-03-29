import contextlib
import time
from itertools import groupby


class DummyProfiler:
    def start(self):
        ...

    def stop(self):
        ...


@contextlib.contextmanager
def profile_it():
    # When pyinstrument is not installed (because we are running in
    # acceptance / production) then this should not fail, just be a
    # null context manager.
    try:
        from pyinstrument import Profiler
    except ImportError:
        yield DummyProfiler()
    else:
        p = Profiler()
        p.start()
        yield p
        p.stop()
        p.print()


@contextlib.contextmanager
def time_it(msg):
    start = time.time()
    yield
    duration = time.time() - start
    print(f'{msg:<24} | {round(duration, 3)} seconds')


def sort_and_group_by(items, key):
    return groupby(sorted(items, key=key), key=key)
