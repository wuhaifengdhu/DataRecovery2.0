#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


class TextHelper(object):
    @staticmethod
    def get_data_length(element):
        try:
            return len(element)
        except TypeError:
            return len(str(element))

    @staticmethod
    def to_string(element):
        try:
            return str(element)
        except UnicodeEncodeError:
            return element

