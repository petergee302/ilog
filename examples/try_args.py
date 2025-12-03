#!/bin/env python3

# Copyright © 2025 Peter Gee
# MIT License
"""
Combine with command-line arguments
"""
from   argparse import ArgumentParser, Namespace
import ilog

logger :ilog.IndentedLogger

def fun(cl_args: Namespace):
    logger.trace(f'> fun({cl_args})')
    # do your job
    logger.trace(f'< fun()')


if __name__ == '__main__':
    parser = ArgumentParser('executable [OPTIONS]')
    # declare your arguments
    parser.add_argument('-v', '--verbosity',
        choices = ilog.LEVEL_NAMES,
           type = str,
        default = ilog.DEFAULT_VERBOSITY_LEVEL,
           help = f'Verbosity level. ' \
                + f'Defaults to `{ilog.DEFAULT_VERBOSITY_LEVEL}`, and overrides `ARXIVRE_LOGGING_LEVEL` if set.'
    )
    cl_args = parser.parse_args()
    with ilog.Setup(cl_args.verbosity, __file__) as logger:
        fun(cl_args)
