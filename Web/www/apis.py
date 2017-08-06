#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'syuson'

'''
JSON API definition
'''

import json, logging, inspect, functools


class APIError(Exception):
    def __init__(self, error, data="", message=""):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class APIValueError(APIError):
    def __init__(self, field, message=""):
        super(APIValueError, self).__init__('Value: invalid', field, message)


class APIResourceNotfoundError(APIError):
    def __init__(self, field, message=""):
        super(APIResourceNotfoundError, self).__init__("Value: Notfound",
                                                       field, message)


class APIPermissionError(APIError):
    def __init__(self, message=""):
        super(APIPermissionError, self).__init__("Permission: forbidden",
                                                 "Permission", message)
