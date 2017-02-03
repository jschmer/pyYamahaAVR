#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from .exception import *
from .util import get_module_logger
from .avr import YamahaAPI

# Register a 'do-nothing' handler to avoid the
# 'No handlers could be found for logger "xyz"' message
# in case of log messages >= WARNING and the client didn't configure logging
get_module_logger().addHandler(logging.NullHandler())

__all__ = [
    'AVRException',
    'CommandNotAvailableException',
    'ConfigException',
    'ParameterMissingException',
    'RequestException',
    'ResponseException',
    'ValueNotSupportedException',
    'YamahaAPI',
]