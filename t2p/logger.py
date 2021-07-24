"""
This module defines the object ``logger`` and its formatter according of the
environment variable ``T2P_ENV``. For *development* the message logs will be
more detailed, but for *production* this will be tiny.
"""

import logging
import sys
import os

T2P_ENV = os.environ.get('T2P_ENV')

logger = logging.getLogger('T2P')

if T2P_ENV == 'development':
    formatter = logging.Formatter(
        '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) ' +
        '[%(module)s.%(funcName)s] %(levelname)s - %(name)s: "%(message)s"'
    )
    level = logging.DEBUG
else:
    formatter = logging.Formatter(
        '[%(levelname)s] - %(name)s: %(message)s'
    )
    level = logging.INFO

console_output_handler = logging.StreamHandler(sys.stderr)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)

logger.setLevel(level)
