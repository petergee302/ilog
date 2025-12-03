# Copyright © 2018-2025 Peter Gee
# MIT License
"""
Indentation, coloring, output format, and additional levels.
"""

from   logging import FATAL, ERROR, WARNING, INFO, DEBUG, Logger
import os
from   typing  import Any


OFF   = 60 # must be above FATAL = 50
TRACE = 15 # between DEBUG and INFO

LEVEL_NAME_2_VALUE = {
        'off': OFF,     # missing from standard logger
      'fatal': FATAL,   # fatal() == critical() already, but the level is called 'CRITICAL'
      'error': ERROR,
    'warning': WARNING,
       'info': INFO,
      'trace': TRACE,
      'debug': DEBUG
}
LEVEL_NAMES  = list(LEVEL_NAME_2_VALUE.keys())
LEVEL_VALUES = list(LEVEL_NAME_2_VALUE.values())



class IndentedLogger(Logger):

    indent :str = ''
    """
    Indentation level
    """

    master_pid :int = 0
    """
    The multiprocessing module uses pipes to communicate with the the subprocesses. This is fine as long
    as the parties DO NOT write to the same output file(s), like the logger handlers do. Otherwise it
    causes random deadlocks in the subprocess' flush() operation, see e.g.:
        https://stackoverflow.com/questions/33886406/how-to-avoid-the-deadlock-in-a-subprocess-without-using-communicate
        https://stackoverflow.com/questions/46447749/python-subprocess-stdout-program-deadlocks
        https://stackoverflow.com/questions/54766479/logging-multithreading-deadlock-in-python
    For that reason the logger should be used in the master process only, whereas by 'master' we mean
    the one creating Setup object.
    """

    master_refs :int = 0
    """
    Reference count used in nested setups
    """

    def _log(self,
             level :int,
               msg :object,
              args :Any,
          exc_info :object | None = None,
             extra :object | None = None,
        stack_info :bool = False,
        stacklevel :int = 1
    ):
        """
        Overridden instance method for generating log messages. Added support for indentation and
        local level.

        In order to generate indent within a block prefix the first message in a function/method
        with '>' character, and the last one with its opposite '<'. For example:

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

        will result in something like:

            DEBUG 2025-03-08 12:17:35.236 > fun()
            DEBUG 2025-03-08 12:17:35.237   > gun(arg=2)
            DEBUG 2025-03-08 12:17:35.238     hun(arg=3): 16
            DEBUG 2025-03-08 12:17:35.239   < gun(): 80
            DEBUG 2025-03-08 12:17:35.240 < fun(): 26

        Notice that it's important to take care about where the '>' and '<' logs are placed.
        Ideally, they should appear at the entry and exit points respectively. Multiple return
        statements are discouraged, as they require careful placing of '<' markers in order to
        keep the log coherent. This raises the difficulty in code maintenance.

        Args:
            level [in]:
                Logging level, from {DEBUG,...,OFF}
            msg [in]:
                Message format
            args [in]:
                Message arguments, can be empty
            exc_info [in]:
                Internal use
            extra [in]:
                Internal use
            stack_info [in]:
                Internal use
            stacklevel [in]:
                Internal use
        """
        if IndentedLogger.master_pid == os.getpid():
            if level >= self.level:
                if not isinstance(msg, str):
                    msg = str(msg)
                if msg.startswith('< '):
                    if len(IndentedLogger.indent) >= 2:
                        # unindent
                        IndentedLogger.indent = IndentedLogger.indent[:-2]
                    else:
                        # remove unbalanced marker
                        msg = msg[2:]
                super()._log(level, IndentedLogger.indent + msg, args, exc_info, extra, stack_info, stacklevel) # pyright: ignore
                if msg.startswith('> ') and len(IndentedLogger.indent) < 80:
                    IndentedLogger.indent += '  '

    def trace(self, msg :str, *args :Any, **kwargs):
        """
        Instance method for TRACE level
        """
        if self.isEnabledFor(TRACE):
            # pylint: disable = protected-access
            self._log(TRACE, msg, args, **kwargs)

    def setLocalLevel(self, level :str | int):
        """
        Set local threshold for the logger. The effective level is the maximum of the two, e.g.:

            local  global  effective
            -----  ------  ---------
            DEBUG  INFO    INFO
            ERROR  INFO    ERROR
        """
        if isinstance(level, str):
            level = LEVEL_NAME_2_VALUE[level]
        self.level = level
