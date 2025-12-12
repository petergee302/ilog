# Copyright © 2018-2025 Peter Gee
# MIT License
"""
Configuration and fetching utilities
"""

import inspect
from   logging import (
    FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET,
    FileHandler, Formatter,
    getLogger as _getLogger, addLevelName
)
from   logging import config
import os
from   pathlib import Path
import traceback
from   types   import TracebackType
# 3rd party
try:
    import numpy as np # pyright: ignore[reportMissingImports]
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
# project
from ilog.utils import timestamp_string
from ilog.constants import TEXT_ENCODING, FILENAME_EXT
from ilog.defaults import (
    DEFAULT_NAMESPACE,
    DEFAULT_COLORIZE,
    DEFAULT_LINE_FORMAT,
    DEFAULT_VERBOSITY_LEVEL
)
from ilog.indented_logger import (
    OFF, TRACE, LEVEL_NAME_2_VALUE,
    IndentedLogger
)

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

_namespace = DEFAULT_NAMESPACE
"""
Safe bet
"""

def getLogger(
    module_name :str | None = None,
          level :str | int  = DEFAULT_VERBOSITY_LEVEL,
      namespace :str | None = None
) -> IndentedLogger:
    """
    Extend the functionality of standard getLogger() function by adding local level.

    Args:
        module_name [in]:
            Used to localize the logging level within the module. If provided, the level may be
            different than the default.
        level [in]:
            Local verbosity levels are effective if higher than the global one, for example:

                local  global  effective
                -----  ------  ---------
                DEBUG  INFO    INFO
                ERROR  INFO    ERROR
    """
    if namespace is None:
        if _namespace is None:
            if ((frame := inspect.currentframe())
            and (module := inspect.getmodule(frame.f_back))):
                namespace = module.__name__.split('.')[0]
            else:
                raise ValueError('Logger namespace cannot be empty. Either set the `ILOG_NAMESPACE` environment variable or pass the `namespace` argument.')
        else:
            namespace = _namespace
    logger_name = namespace
    # prefix module name with project, if set
    if module_name not in {None, '__main__'}:
        # to avoid overriding local level by one of the parent modules (guess which one)
        # all local loggers have project logger as direct parent
        module_name = str(module_name).replace('.', '/')
        logger_name += '.' +  module_name
    local_logger = _getLogger(logger_name)
    assert isinstance(local_logger, IndentedLogger)
    # customize local level
    local_logger.setLocalLevel(level)
    return local_logger


class Setup:
    def __init__(self, global_level :str | int  = NOTSET,
                        output_path :str | None = None,
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
            output_path [in]:
                Where to save the log file: This can be either complete file path, or a directory.
                in the latter case module_fname is required.
            module_fname [in]:
                If given, its base name will be combined with given directory path and extension to
                build module-related log file. For instance `train.py` will become
                    `<output_path>/train.log`
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

        if output_path:
            log_bpath, log_ext = os.path.splitext(output_path)
            if log_ext == FILENAME_EXT:
                # assume complete file path
                log_fpath = output_path
            else:
                # try to build file path
                if module_fname in {None, '__main__'}:
                    # replace extension to not overwrite the module itself
                    log_fpath = f'{log_bpath}-{timestamp_string()}{FILENAME_EXT}'
                else:
                    # treat output_path as directory path, and combine it with module name and extension
                    module_name, _ = os.path.splitext(os.path.basename(str(module_fname))) # pacify linter
                    log_fpath = os.path.join(log_bpath, f'{module_name}-{timestamp_string()}{FILENAME_EXT}')
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
                raise ValueError('Logger namespace cannot be empty. Either set the `ILOG_NAMESPACE` environment variable or pass the `namespace` argument.')

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
