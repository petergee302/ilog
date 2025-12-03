# Copyright © 2018-2025 Peter Gee
# MIT License
"""
Indentation, coloring, output format, and additional levels.
"""
from logging import (
    FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET,
    setLoggerClass
)
from ilog.constants import TEXT_ENCODING, FILENAME_EXT
from ilog.defaults import (
    DEFAULT_NAMESPACE,
    DEFAULT_COLORIZE,
    DEFAULT_LINE_FORMAT,
    DEFAULT_VERBOSITY_LEVEL
)
from ilog.indented_logger import (
    OFF, TRACE, LEVEL_NAME_2_VALUE, LEVEL_NAMES, LEVEL_VALUES,
    IndentedLogger
)
from ilog.setup import Setup, getLogger
from ilog.decorators import (
    repr,
        log_function_call,
      fatal_function_call,
      error_function_call,
    warning_function_call,
       info_function_call,
      trace_function_call,
      debug_function_call,
          log_method_call,
        fatal_method_call,
        error_method_call,
      warning_method_call,
         info_method_call,
        trace_method_call,
        debug_method_call,
                 log_calls,
               fatal_calls,
               error_calls,
             warning_calls,
                info_calls,
               trace_calls,
               debug_calls,
        log_function_block,
      fatal_function_block,
      error_function_block,
    warning_function_block,
       info_function_block,
      trace_function_block,
      debug_function_block,
          log_method_block,
        fatal_method_block,
        error_method_block,
      warning_method_block,
         info_method_block,
        trace_method_block,
        debug_method_block,
                 log_blocks,
               fatal_blocks,
               error_blocks,
             warning_blocks,
                info_blocks,
               trace_blocks,
               debug_blocks
)

setLoggerClass(IndentedLogger)
