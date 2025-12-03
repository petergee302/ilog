#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
"""
Example of nested function calls with indentation.
"""

import ilog

# NOTE this global logger variable is left uninitialized until Setup.__enter__() call. We can afford
# this here because it's not used beforehand; when using wrappers this would not be acceptable.
logger :ilog.IndentedLogger


def fun() -> int:
    logger.debug('> fun()')
    result = gun(2)//3
    logger.debug('< fun(): %d', result)
    return result


def gun(arg :int) -> int:
    logger.debug('> gun(arg=%d)', arg)
    result = 5*hun(arg + 1)
    logger.debug('< gun(): %d', result)
    return result


def hun(arg :int) -> int:
    result = 13 + arg
    logger.debug('hun(arg=%d): %d', arg, result)
    return result


if __name__ == '__main__':
    with ilog.Setup(ilog.DEBUG) as logger:
        fun()
