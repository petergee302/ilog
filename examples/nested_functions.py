#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
"""
Nested function calls
"""

import ilog

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
