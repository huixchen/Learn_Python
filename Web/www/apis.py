#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'syuson'

'''
JSON API definition
'''

import json,logging,inspect,functools

class APIError(Exception):
	pass
