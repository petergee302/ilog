#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
"""
Example of nested function calls with indentation and automatic logging.
"""

import ilog

# NOTE if the namespace is left empty, it will be derived from the module name, which is '__main__'
# when run as a script, but would be different when imported. To have a consistent namespace, we
# set it here explicitly.
ILOG_NAMESPACE = 'examples'
logger = ilog.getLogger(namespace = ILOG_NAMESPACE)


@ilog.info_function_block(logger)
def fun() -> int:
    result = gun(2)//3
    return result


@ilog.trace_function_block(logger)
def gun(arg :int) -> int:
    result = 5*hun(arg + 1)
    return result


@ilog.debug_function_call(logger)
def hun(arg :int) -> int:
    result = 13 + arg
    return result


if __name__ == '__main__':
    with ilog.Setup(ilog.DEBUG, namespace = ILOG_NAMESPACE) as logger:
        fun()
