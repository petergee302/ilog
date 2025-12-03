#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
import os
from   random import randint, random
import sys
# make this script runnable from any location
ROOT_RDPATH = os.path.relpath(__file__ + '/../..', os.getcwd()) + '/'
assert os.path.isfile(ROOT_RDPATH + 'pyproject.toml')
if ROOT_RDPATH not in sys.path:
    sys.path.append(ROOT_RDPATH)
# one of two methods to set the namespace:
ILOG_NAMESPACE = 'tests'
os.environ['ILOG_NAMESPACE'] = ILOG_NAMESPACE
# local imports
import ilog
from   examples.try_wrapped_methods import AutoA, AutoB

logger = ilog.getLogger()

LOCAL_FPATH = ROOT_RDPATH + 'temp' + ilog.FILENAME_EXT


@ilog.trace_blocks(logger)
class AutoC(AutoA):
    """
    Another derived class to make more of variation
    """

    def gun(self, c :int) -> int:
        return int(float(self.hun(c))*2.0)

def test_fetching():
    """
    Ensure that getLogger() fetches the same logger instance for the same name. The loggers'
    hierarchy in this example is as follows:

        root                    # stadard Logger
         └─ tests               # IndentedLogger
             ├─ tests.abc       # IndentedLogger
             └─ tests.abc/def   # IndentedLogger
    """
    logger1 = ilog.getLogger('__main__')
    logger2 = ilog.getLogger()
    assert logger1 is logger2
    logger3 = ilog.getLogger('abc')
    assert logger3.parent is logger1
    # NOTE: this is excursion from the standard logging behavior, wherein the parent of 'abc.def'
    # would be 'abc'. Here we always set the project logger as the parent of all sub-module loggers,
    # with flat dependence
    logger4 = ilog.getLogger('abc.def')
    assert logger4.parent is logger1
    assert logger4 is not logger3


def test_method_wrappers():
    TEST_CASES = {
        ilog.OFF     : 0,
        ilog.FATAL   :10,   # 10 fatalities
        ilog.ERROR   :30,   # 20 errors
        ilog.WARNING :40,   # 10 warnings
        ilog.INFO    :46,   #  6 infos
        ilog.TRACE   :57,   # 11 traces
        ilog.DEBUG   :71    # 14 debugs
    }
    for level in ilog.LEVEL_VALUES:
        # clear any past log output
        if os.path.isfile(LOCAL_FPATH):
            os.remove(LOCAL_FPATH)
        with ilog.Setup(level, LOCAL_FPATH):
            objects = [
                AutoA(10),
                AutoB(10),
                AutoC(21),
                AutoB(21),
                AutoA( 7),
            ]
            for o in objects:
                o.fun(13)
        if level == ilog.OFF:
            assert not os.path.isfile(LOCAL_FPATH)
            n_lines = 0
        else:
            with open(LOCAL_FPATH, 'rt', encoding = ilog.TEXT_ENCODING) as log_file:
                n_lines = len(log_file.readlines())
        print(f'Level {level}: logged {n_lines} lines')
        assert n_lines == TEST_CASES[level]
    # clean-up
    os.remove(LOCAL_FPATH)


if __name__ == '__main__':
    test_fetching()
    test_method_wrappers()
