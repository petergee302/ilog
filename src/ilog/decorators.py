# Copyright © 2018-2025 Peter Gee
# MIT License
"""
Function, method, and class decorators for logging calls and indented blocks.

    <level>_function_call(),
        log arguments and return value and on exit
    <level>_method_call():
        as above, but prefix method name with class name and object ID
    <level>_function_block(),
        indent block between entry/exit points, log arguments on entry, return value on exit
    <level>_method_block():
        as above, indent block between entry/exit points, log arguments on entry, return value on exit
    <level>_calls()
        apply <level>_method_call() to all methods of a class
    <level>_blocks()
        apply <level>_method_block() to all methods of a class

Where <level> is one of:
    fatal, error, warning, info, trace, debug
"""
from functools import wraps
from logging import FATAL, ERROR, WARNING, INFO, DEBUG
from typing import Any
# 3rd party
try:
    import numpy as np # pyright: ignore[reportMissingImports]
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
try:
    import pandas as pd # pyright: ignore[reportMissingImports]
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
try:
    import polars as pl # pyright: ignore[reportMissingImports]
    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False
try:
    import torch # pyright: ignore[reportMissingImports]
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
from ilog.indented_logger import TRACE, IndentedLogger


def repr(x: Any | None):
    """
    Generate short string description of a numpy/torch/pandas/polars/other multi-array for logging
    purposes.
    """
    if ((HAS_NUMPY  and isinstance(x, np.ndarray))       # pyright: ignore[reportPossiblyUnboundVariable]
    or  (HAS_TORCH  and isinstance(x, torch.Tensor))     # pyright: ignore[reportPossiblyUnboundVariable]
    or  (HAS_PANDAS and isinstance(x, pd.DataFrame))):   # pyright: ignore[reportPossiblyUnboundVariable]
        return f'{{shape={x.shape}, dtype={x.dtype}}}'   # pyright: ignore[reportOptionalMemberAccess]
    elif (HAS_POLARS  and isinstance(x, pl.DataFrame)):  # pyright: ignore[reportPossiblyUnboundVariable]
        return f'{{shape={x.shape}, dtypes={x.dtypes}}}' # pyright: ignore[reportOptionalMemberAccess]
    elif x is None:
        return 'None'
    elif type(x) in {int, float, str, bool, list, tuple, dict}:
        return str(x)
    else:
        return f'{type(x).__name__}[{id(x):012X}]'


def log_function_call(logger :IndentedLogger, level :int = TRACE):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            if level >= logger.level and logger.isEnabledFor(level):
                args_str   = ', '.join(repr(a) for a in args)
                kwargs_str = ', '.join(f'{k}={repr(v)}' for k, v in kwargs.items())
                if args_str and kwargs_str:
                    args_str += ', '
                if result is not None:
                    result_str = ': ' + repr(result)
                else:
                    result_str = ''
                msg = f'{function.__name__}({args_str}{kwargs_str}){result_str}'
                logger._log(level, msg, [], {}) # pyright: ignore[reportPrivateUsage]
            return result
        return wrapper
    return decorator


def fatal_function_call(logger :IndentedLogger):
    return log_function_call(logger, FATAL)


def error_function_call(logger :IndentedLogger):
    return log_function_call(logger, ERROR)


def warning_function_call(logger :IndentedLogger):
    return log_function_call(logger, WARNING)


def info_function_call(logger :IndentedLogger):
    return log_function_call(logger, INFO)


def trace_function_call(logger :IndentedLogger):
    return log_function_call(logger, TRACE)


def debug_function_call(logger :IndentedLogger):
    return log_function_call(logger, DEBUG)


def log_function_block(logger :IndentedLogger, level :int = TRACE):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            emit_messages = level >= logger.level and logger.isEnabledFor(level)
            function_name = function.__name__
            if emit_messages:
                args_str   = ', '.join(repr(a) for a in args)
                kwargs_str = ', '.join(f'{k}={repr(v)}' for k, v in kwargs.items())
                if args_str and kwargs_str:
                    args_str += ', '
                msg = f'> {function_name}({args_str}{kwargs_str})'
                logger._log(level, msg, [], {}) # pyright: ignore[reportPrivateUsage]
            result = function(*args, **kwargs)
            if emit_messages:
                if result is not None:
                    result_str = ': ' + repr(result)
                else:
                    result_str = ''
                msg = f'< {function_name}(){result_str}'
                logger._log(level, msg, [], {}) # pyright: ignore[reportPrivateUsage]
            return result
        return wrapper
    return decorator


def fatal_function_block(logger :IndentedLogger):
    return log_function_block(logger, level = FATAL)


def error_function_block(logger :IndentedLogger):
    return log_function_block(logger, level = ERROR)


def warning_function_block(logger :IndentedLogger):
    return log_function_block(logger, level = WARNING)


def info_function_block(logger :IndentedLogger):
    return log_function_block(logger, level = INFO)


def trace_function_block(logger :IndentedLogger):
    return log_function_block(logger, level = TRACE)


def debug_function_block(logger :IndentedLogger):
    return log_function_block(logger, level = DEBUG)


def log_method_call(logger :IndentedLogger, level :int = TRACE):
    def decorator(method):
        @wraps(method)
        def wrapper(instance, *args, **kwargs):
            result = method(instance, *args, **kwargs)
            if level >= logger.level and logger.isEnabledFor(level):
                method_name = '' if method.__name__ == '__init__' else '.' + method.__name__
                args_str   = ', '.join(repr(a) for a in args)
                kwargs_str = ', '.join(f'{k}={repr(v)}' for k, v in kwargs.items())
                if args_str and kwargs_str:
                    args_str += ', '
                if result is not None:
                    result_str = ': ' + repr(result)
                else:
                    result_str = ''
                msg = f'{type(instance).__name__}[{id(instance):012X}]{method_name}({args_str}{kwargs_str}){result_str}'
                logger._log(level, msg, [], {}) # pyright: ignore[reportPrivateUsage]
            return result
        return wrapper
    return decorator


def fatal_method_call(logger :IndentedLogger):
    return log_method_call(logger, level = FATAL)


def error_method_call(logger :IndentedLogger):
    return log_method_call(logger, level = ERROR)


def warning_method_call(logger :IndentedLogger):
    return log_method_call(logger, level = WARNING)


def info_method_call(logger :IndentedLogger):
    return log_method_call(logger, level = INFO)


def trace_method_call(logger :IndentedLogger):
    return log_method_call(logger, level = TRACE)


def debug_method_call(logger :IndentedLogger):
    return log_method_call(logger, level = DEBUG)


def log_method_block(logger :IndentedLogger, level :int = TRACE):
    def decorator(method):
        @wraps(method)
        def wrapper(instance, *args, **kwargs):
            emit_messages = level >= logger.level and logger.isEnabledFor(level)
            method_name = ''
            if emit_messages:
                if method.__name__ != '__init__':
                    method_name = '.' + method.__name__
                args_str   = ', '.join(repr(a) for a in args)
                kwargs_str = ', '.join(f'{k}={repr(v)}' for k, v in kwargs.items())
                if args_str and kwargs_str:
                    args_str += ', '
                msg = f'> {type(instance).__name__}[{id(instance):012X}]{method_name}({args_str}{kwargs_str})'
                logger._log(level, msg, [], {}) # pyright: ignore[reportPrivateUsage]
            result = method(instance, *args, **kwargs)
            if emit_messages:
                if result is not None:
                    result_str = ': ' + repr(result)
                else:
                    result_str = ''
                msg = f'< {type(instance).__name__}[{id(instance):012X}]{method_name}(){result_str}'
                logger._log(level, msg, [], {}) # pyright: ignore[reportPrivateUsage]
            return result
        return wrapper
    return decorator


def fatal_method_block(logger :IndentedLogger):
    return log_method_block(logger, level = FATAL)


def error_method_block(logger :IndentedLogger):
    return log_method_block(logger, level = ERROR)


def warning_method_block(logger :IndentedLogger):
    return log_method_block(logger, level = WARNING)


def info_method_block(logger :IndentedLogger):
    return log_method_block(logger, level = INFO)


def trace_method_block(logger :IndentedLogger):
    return log_method_block(logger, level = TRACE)


def debug_method_block(logger :IndentedLogger):
    return log_method_block(logger, level = DEBUG)


def log_calls(logger :IndentedLogger, level :int = TRACE):
    def class_decorator(cls):
        for name, attribute in cls.__dict__.items():
            if callable(attribute) and not name.startswith("__"):
                setattr(cls, name, log_method_call(logger, level)(attribute))
        return cls
    return class_decorator


def fatal_calls(logger :IndentedLogger):
    return log_calls(logger, level = FATAL)


def error_calls(logger :IndentedLogger):
    return log_calls(logger, level = ERROR)


def warning_calls(logger :IndentedLogger):
    return log_calls(logger, level = WARNING)


def info_calls(logger :IndentedLogger):
    return log_calls(logger, level = INFO)


def trace_calls(logger :IndentedLogger):
    return log_calls(logger, level = TRACE)


def debug_calls(logger :IndentedLogger):
    return log_calls(logger, level = DEBUG)


def log_blocks(logger :IndentedLogger, level :int = TRACE):
    def class_decorator(cls):
        for name, attribute in cls.__dict__.items():
            if callable(attribute) and not name.startswith("__"):
                setattr(cls, name, log_method_block(logger, level)(attribute))
        return cls
    return class_decorator


def fatal_blocks(logger :IndentedLogger):
    return log_blocks(logger, level = FATAL)


def error_blocks(logger :IndentedLogger):
    return log_blocks(logger, level = ERROR)


def warning_blocks(logger :IndentedLogger):
    return log_blocks(logger, level = WARNING)


def info_blocks(logger :IndentedLogger):
    return log_blocks(logger, level = INFO)


def trace_blocks(logger :IndentedLogger):
    return log_blocks(logger, level = TRACE)


def debug_blocks(logger :IndentedLogger):
    return log_blocks(logger, level = DEBUG)
