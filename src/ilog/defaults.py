# Copyright © 2025 Peter Gee
# MIT License
"""
Default argument values that can be overridden in the environment
"""
import os
from   ilog.utils import boolean_type

DEFAULT_NAMESPACE = os.getenv('ILOG_NAMESPACE', None)
"""
Name-space used to separate messages in the log stream. Typically this should be a short name of
your project; if not specified, the ilog.Setup() will attempt to extract it from the calling
module's name.
"""

DEFAULT_COLORIZE = boolean_type(os.getenv('ILOG_COLORIZE', str(os.name != "nt")))
"""
Whether to apply ANSI colors to the severity levels. By default this option is enabled on all
terminals except Windows, where CMD.exe does not support them.
"""

DEFAULT_LINE_FORMAT = os.getenv('ILOG_LINE_FORMAT', "%(levelname)s %(asctime)s.%(msecs)03d %(thread)012X %(message)s")
"""
The default line format prefixes each message with severity level, ISO dat-time up to millisecond
resolution and thread handle. The latter gets very useful when debugging multi-threaded
applications where messages from parallel threads get mixed into single stream, and may otherwise be
hard to make sense of.

    DEBUG 2025-11-24 15:15:18.594 7036CCD1D080 <your message here>
"""

DEFAULT_VERBOSITY_LEVEL = os.getenv('ILOG_VERBOSITY_LEVEL', 'trace')
"""
Set the verbosity depending on the phase of your project. Use `debug` initially, and raise to `info`
or higher the production code.
"""
