# Copyright © 2020-2025 Peter Gee
# MIT License
from argparse import ArgumentTypeError
from datetime import datetime

def timestamp_string() -> str:
    """
    Generate a timestamp string in the format YYYYMMDDHHMMSSFFF
    """
    now = datetime.now()
    return now.strftime('%Y%m%d%H%M%S') + f'{now.microsecond//1000:03d}'


def boolean_type(argument_string: str) -> bool:
    """
    Convert command-line or environment string to Boolean value.
    """
    if argument_string.lower() in {'true', '1', 'yes', 'y', 'on'}:
        return True
    if argument_string.lower() in {'false', '0', 'no', 'n', 'off'}:
        return False
    raise ArgumentTypeError(
        f'Expecting Boolean value (true/false), not `{argument_string}`.'
    )
