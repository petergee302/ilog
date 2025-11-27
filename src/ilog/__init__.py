# Copyright © 2018-2025 Peter Gee
# MIT License
"""
Indentation, coloring, output format, and additional levels.
"""

import os
import inspect
from   logging import (
    FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET,
    FileHandler, Formatter, Logger,
    getLogger as _getLogger, addLevelName, setLoggerClass
)
from   logging import config
from   typing  import Any
from   pathlib import Path
import traceback
from   types   import TracebackType
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
# project
from ilog.utils import timestamp_string
from ilog.constants import TEXT_ENCODING, FILENAME_EXT
from ilog.defaults import (
    DEFAULT_NAMESPACE,
    DEFAULT_COLORIZE,
    DEFAULT_LINE_FORMAT,
    DEFAULT_VERBOSITY_LEVEL
)

_namespace = DEFAULT_NAMESPACE
"""
Safe bet
"""

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
LEVELS = list(LEVEL_NAME_2_VALUE.keys())

_DEFAULT_LOGGING_OPTS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    },
}


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

    local_level :int = NOTSET
    """
    Local verbosity level
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
            if level >= self.local_level:
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

    def setLocalLevel(self, local_level :str | int):
        """
        Set local threshold for the logger. The effective level is the maximum of the two, e.g.:

            local  global  effective
            -----  ------  ---------
            DEBUG  INFO    INFO
            ERROR  INFO    ERROR
        """
        if isinstance(local_level, str):
            local_level = LEVEL_NAME_2_VALUE[local_level]
        self.local_level = local_level

setLoggerClass(IndentedLogger)


def getLogger(
    module_name :str | None = None,
    local_level :str | int  = DEFAULT_VERBOSITY_LEVEL
) -> IndentedLogger:
    """
    Extend the functionality of standard getLogger() function by adding local level.

    Args:
        module_name [in]:
            Used to localize the logging level within the module. If provided, the level may be
            different than the default.
        local_level [in]:
            Local verbosity levels are effective if higher than the global one, for example:

                local  global  effective
                -----  ------  ---------
                DEBUG  INFO    INFO
                ERROR  INFO    ERROR
    """
    # prefix module name with project, if set
    if module_name:
        # to avoid overriding local level by one of the parent modules (guess which one)
        # all local loggers have project logger as direct parent
        module_name = module_name.replace('.', '/')
        if _namespace:
            namespace = '.'.join([_namespace, module_name])
        else:
            namespace = module_name
    else:
        namespace = _namespace

    local_logger = _getLogger(namespace)

    assert isinstance(local_logger, IndentedLogger)
    # customize local level
    local_logger.setLocalLevel(local_level)
    return local_logger


class Setup:
    def __init__(self, global_level :str | int  = NOTSET,
                           log_path :str | None = None,
                       module_fname :str | None = None,
                          namespace :str | None = DEFAULT_NAMESPACE,
                           colorize :bool       = DEFAULT_COLORIZE,
                        line_format :str        = DEFAULT_LINE_FORMAT
    ):
        """
        Sets up the logger and enables logging to a file if requested.

        Args:
            global_level [in]:
                Verbosity level to set for the logger. Can be either the name or the numerical value
                corresponding to the level. The default value of `logging.NOTSET` does not change
                current threshold.
            log_path [in]:
                Where to save the log file: This can be either complete file path, or a directory.
                in the latter case module_fname is required.
            module_fname [in]:
                If given, its base name will be combined with given directory path and extension to
                build module-related log file. For instance `train.py` will become
                    `<log_path>/train.log`
            namespace [in]:
                If given, overrides the namespace
            colorize [in]:
                Enable/disable colored console output (notice, if enabled the escape sequences also
                appear in the file)
            line_format [in]:
                Message prefix to override the default format.
        """
        if isinstance(global_level, str):
            global_level = LEVEL_NAME_2_VALUE[global_level]

        if log_path:
            if module_fname is None:
                # assume complete file path
                if log_path.endswith(FILENAME_EXT):
                    log_fpath = log_path
                else:
                    # replace extension (don't overwrite module itself :)
                    log_bpath, _ = os.path.splitext(log_path)
                    log_fpath = f'{log_bpath}-{timestamp_string()}{FILENAME_EXT}'
            else:
                # treat log_path as directory path, and combine it with module name and extension
                module_name, _ = os.path.splitext(os.path.basename(module_fname))
                log_fpath = os.path.join(log_path, f'{module_name}-{timestamp_string()}{FILENAME_EXT}')
        else:
            log_fpath = None
        self.global_level = global_level
        self.   log_fpath = log_fpath
        self.    colorize = colorize
        self. line_format = line_format

        if namespace is None:
            if ((frame := inspect.currentframe())
            and (module := inspect.getmodule(frame.f_back))):
                namespace = module.__name__.split('.')[0]
            else:
                namespace = 'ilog' # last resort

        global _namespace
        _namespace = namespace
        if HAS_NUMPY:
            np.set_printoptions(precision = 3, linewidth = 140, suppress = True, sign = ' ') # pyright: ignore[reportPossiblyUnboundVariable]

    def __enter__(self) -> IndentedLogger:
        """
        Begin of protected scope.
        """
        setup_master = (IndentedLogger.master_refs == 0)
        IndentedLogger.master_refs += 1
        if IndentedLogger.master_pid == 0:
            IndentedLogger.master_pid = os.getpid()
        project_logger = _getLogger(_namespace)
        assert isinstance(project_logger, IndentedLogger)
        if self.global_level: # != {None, '', logging.NOTSET, 0}
            project_logger.disabled = self.global_level == OFF
            if not project_logger.disabled:
                if self.log_fpath:
                    Path(self.log_fpath).parent.mkdir(parents = True, exist_ok = True)

                if self.colorize:
                    addLevelName(OFF,     "OFF")
                    addLevelName(FATAL,   "💀 \33[0;35mFATAL  \33[0;37m")
                    addLevelName(ERROR,   "💥 \33[0;31mERROR  \33[0;37m")
                    addLevelName(WARNING, "⚠️ \33[0;93mWARNING\33[0;37m")
                    addLevelName(INFO,    "💬 \33[0;97mINFO   \33[0;37m")
                    addLevelName(TRACE,   "🐾 \33[0;32mTRACE  \33[0;37m")
                    addLevelName(DEBUG,   "🔎 \33[0;96mDEBUG  \33[0;37m")
                else:
                    addLevelName(OFF,     "OFF")
                    addLevelName(FATAL,   "💀 FATAL  ")
                    addLevelName(ERROR,   "💥 ERROR  ")
                    addLevelName(WARNING, "⚠️ WARNING")
                    addLevelName(INFO,    "💬 INFO   ")
                    addLevelName(TRACE,   "🐾 TRACE  ")
                    addLevelName(DEBUG,   "🔎 DEBUG  ")

                if setup_master:
                    opts = _DEFAULT_LOGGING_OPTS.copy()
                    opts["formatters"]["default"]["format"] = self.line_format
                    config.dictConfig(opts)
                if self.log_fpath:
                    file_handler = FileHandler(
                        filename = self.log_fpath,
                            mode = 'w',
                        encoding = TEXT_ENCODING
                    )
                    file_handler.setFormatter(Formatter(self.line_format, datefmt = Formatter.default_time_format))
                    project_logger.addHandler(file_handler)
                project_logger.setLevel(self.global_level)
        return project_logger


    def __exit__(self, exc_type :type[BaseException] | None,
                            exc :BaseException       | None,
                  exc_traceback :TracebackType       | None) -> None:
        """
        End of protected scope.

        We usually want to clean-up after the tests and remove temporary logs. But removing
        directory along with the file to which the logger still writes may not be the best idea,
        thus we need to detach the corresponding file handler.

        Args:
            exc_type [in]:
                Unhandled exception type, if any
            exc [in]:
                Unhandled exception, if any
            exc_traceback [in]:
                Stack trace, in case of unhandled exception

        Returns:
            None
        """
        if (self.global_level
        and self.global_level != OFF):
            project_logger = _getLogger(_namespace)
            if exc and exc_type and exc_traceback:
                # log unhandled exception if any
                if issubclass(exc_type, KeyboardInterrupt):
                    if project_logger.isEnabledFor(INFO):
                        logging_fn = project_logger.info
                    else:
                        logging_fn = None
                else:
                    # log the exception at FATAL level
                    if project_logger.isEnabledFor(FATAL):
                        logging_fn = project_logger.fatal
                    else:
                        logging_fn = None
                if logging_fn:
                    x = traceback.format_exception_only(exc)
                    exception_string = ''.join(x)
                    logging_fn(exception_string.rstrip())
                    short_stack_string = ''.join(traceback.format_tb(exc_traceback))
                    logging_fn('Traceback (most recent call last):\n' + short_stack_string.rstrip())
            if (self.log_fpath):
                log_fpath = self.log_fpath
                if log_fpath.startswith("./") or log_fpath.startswith(".\\"):
                    log_fpath = log_fpath[2:]
                for handler in project_logger.handlers[:]:
                    if (isinstance(handler, FileHandler)
                    and handler.baseFilename.endswith(log_fpath)):
                        handler.flush()
                        handler.close()
                        project_logger.removeHandler(handler)
        # dereference
        IndentedLogger.master_refs -= 1
        if IndentedLogger.master_refs == 0:
            IndentedLogger.master_pid = 0


def repr(x: Any | None):
    """
    Generate short string description of a numpy/torch/pandas/polars/other multi-array for logging
    purposes.
    """
    if ((HAS_NUMPY  and isinstance(x, 'np.ndarray'))
    or  (HAS_TORCH  and isinstance(x, 'torch.Tensor'))
    or  (HAS_PANDAS and isinstance(x, 'pd.DataFrame'))):
        return f'{{shape={x.shape}, dtype={x.dtype}}}'   # pyright: ignore[reportOptionalMemberAccess]
    if (HAS_POLARS  and isinstance(x, 'pl.DataFrame')):
        return f'{{shape={x.shape}, dtypes={x.dtypes}}}' # pyright: ignore[reportOptionalMemberAccess]
    if x is None:
        return 'None'
    else:
        return f'{type(x).__name__}[{id(x):012X}]'
