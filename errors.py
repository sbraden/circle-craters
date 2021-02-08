# -*- coding: utf-8 -*-


class CircleCraterError(Exception):
    def __init__(self, message_str = ''):
        self.message = message_str
