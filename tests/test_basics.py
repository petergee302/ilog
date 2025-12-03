#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
import os
import ilog
import sys
# make this script runnable from any location
ROOT_RDPATH = os.path.relpath(__file__ + '/../..', os.getcwd()) + '/'
assert os.path.isfile(ROOT_RDPATH + 'pyproject.toml')
if ROOT_RDPATH not in sys.path:
    sys.path.append(ROOT_RDPATH)

TEST_NAMESPACE = 'ilog.tests'
LOCAL_FPATH = './temp' + ilog.FILENAME_EXT

def test_thresholds():
    """
    Ensure that the threshold mechanism filters out messages below the requested severity level
    """
    def log_all(logger :ilog.IndentedLogger):
        logger.fatal  ('fatal')
        logger.error  ('error')
        logger.warning('warning')
        logger.info   ('info')
        logger.trace  ('trace')
        logger.debug  ('debug')

    for n_enabled, level in enumerate(ilog.LEVEL_VALUES):
        if os.path.isfile(LOCAL_FPATH):
            os.remove(LOCAL_FPATH)
        with ilog.Setup(level, LOCAL_FPATH, namespace = TEST_NAMESPACE) as logger:
            log_all(logger)
            if level != ilog.OFF:
                with open(LOCAL_FPATH, 'rt', encoding = ilog.TEXT_ENCODING) as log_file:
                    n_lines = len(log_file.readlines())
                    assert n_lines == n_enabled
            else:
                assert not os.path.isfile(LOCAL_FPATH)
    # clean-up
    os.remove(LOCAL_FPATH)


def test_indentation():
    """
    Ensure the indent is increasing/decreasing with the markers.
    """
    MIN_INDENT = 1
    MAX_INDENT = 5
    with ilog.Setup(ilog.TRACE, LOCAL_FPATH, namespace = TEST_NAMESPACE) as logger:
        for depth in range(MIN_INDENT, MAX_INDENT + 1):
            prior_indent = ''
            for indent in range(depth):
                logger.trace(f'> level {indent}')
                assert len(prior_indent) < len(logger.indent)
                prior_indent = logger.indent
            for indent in reversed(range(depth)):
                logger.trace(f'< level {indent}')
                assert len(prior_indent) > len(logger.indent)
                prior_indent = logger.indent
    # clean-up
    os.remove(LOCAL_FPATH)


def test_nesting():
    """
    Ensure the loggers can be nested. This is a frequent use case when testing wherein the outer
    setup is part of the the test code, and inner one is an executable script under test.
    """
    OUTER_FPATH = './temp-outer' + ilog.FILENAME_EXT
    INNER_FPATH = './temp-inner' + ilog.FILENAME_EXT
    with ilog.Setup(ilog.TRACE, OUTER_FPATH, namespace = TEST_NAMESPACE) as outer_logger:
        outer_logger.trace(f'> outer')
        with ilog.Setup(ilog.TRACE, INNER_FPATH, namespace = TEST_NAMESPACE) as inner_logger:
            inner_logger.trace(f'inner')
        outer_logger.trace(f'< outer')
    inner_stat = os.stat(INNER_FPATH)
    outer_stat = os.stat(OUTER_FPATH)
    assert inner_stat.st_size*3 <= outer_stat.st_size
    # clean-up
    os.remove(OUTER_FPATH)
    os.remove(INNER_FPATH)


if __name__ == '__main__':
    """
    Debug the tests under IDE
    """
    test_thresholds()
    test_indentation()
    test_nesting()
    pass
