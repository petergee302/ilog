#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
from   random import randint, random
import ilog

logger = ilog.getLogger()


class AutoA:
    """
    Base class to test ilog decorators.

    Use method decorators if you want to quickly add indentation and entry/exit markers, and you're
    happy with the standard content of the messages, i.e.:
        - class name
        - object ID
        - method name
        - argument names and values
        - returned values
    """
    @ilog.trace_method_call(logger)
    def __init__(self, a :int):
        self.a = a

    @ilog.debug_method_block(logger)
    def fun(self, b :int) -> int:
        result = self.gun(self.a + b)
        h = self.hun(result)
        result += int(float(h))
        result += len(self.pun(self.nun(h)))
        return result

    @ilog.trace_method_block(logger)
    def gun(self, c :int) -> int:
        result = self.a*c
        h = int(float(self.hun(random())))
        if randint(0, 2):
            result += h
        return result

    @ilog.info_method_call(logger)
    def hun(self, d :float) -> str:
        return f'{d*(self.a - 1):.3f}'

    @ilog.warning_method_block(logger)
    def nun(self, e :str) -> str:
        return self.pun(e)

    @ilog.error_method_block(logger)
    def pun(self, f :str) -> str:
        arg = (f >= "1.00")
        self.run(arg)
        return "stop" if arg else "GAME OVER"

    @ilog.fatal_method_call(logger)
    def run(self, g :bool) -> None:
        return

@ilog.debug_calls(logger)
class AutoB(AutoA):
    """
    Derived class to use dynamical determination of class names and IDs
    """

    def gun(self, c :int) -> int:
        result = c%self.a
        return result

    def hun(self, d :float) -> str:
        return f'{d/(self.a + 1):.3f}'


if __name__ == '__main__':
    with ilog.Setup(ilog.DEBUG) as logger:
        object_a = AutoA(5)
        object_b = AutoB(10)
        object_a.fun(7)
        object_b.fun(13)
