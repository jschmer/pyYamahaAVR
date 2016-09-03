#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AVRException(Exception):
    pass


class CommandNotAvailableException(AVRException):
    """Exception raised when command is not supported"""
    pass


class RequestException(AVRException):
    """Exception raised when AVR responded with an error code to a request"""
    pass


class ResponseException(AVRException):
    """Exception raised when receiver responded with an error code to a command"""
    pass


class ConfigException(AVRException):
    """Exception raised when AVR command file is ill-formed"""
    pass


class ParameterMissingException(AVRException):
    """Exception raised when AVR PUT command with missing parameter is attempted"""
    pass


class ValueNotSupportedException(AVRException):
    """Exception raised when trying to send an AVR PUT command with a value that is not supported"""
    pass
