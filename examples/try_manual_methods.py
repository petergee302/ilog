#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
"""
Use in objects
"""
import math
import ilog

# NOTE: here we customize the local level, but it gets overridden during Setup() in the main block
# below, because both refer to the same logger named '__main__'. If you want to make the two
# separate, use different module name.
logger = ilog.getLogger(__name__, ilog.TRACE)

class Base:
    _arg1 :int

    def __init__(self, arg1: int):
        logger.trace(f'{type(self).__name__}[{id(self):012X}]({arg1=})')
        self._arg1 = arg1

    def method(self, arg2: bool) -> float:
        if arg2:
            result = math.pi # 3.14159
        else:
            result = math.e  # 2.71828
        result *= self._arg1
        logger.trace(f'{type(self).__name__}[{id(self):012X}].method({arg2=}): {result=}')
        return result

class Derived(Base):
    def method(self, arg2: bool) -> float:
        result = math.sin(int(arg2)*math.sqrt(10))
        logger.debug(f'{type(self).__name__}[{id(self):012X}].method({arg2=}): {result=}')
        return result


if __name__ == '__main__':
    with ilog.Setup(ilog.DEBUG) as logger:
        base = Base(5)
        derived = Derived(10)
        base   .method(True)
        derived.method(True)
        base   .method(False)
        derived.method(False)
