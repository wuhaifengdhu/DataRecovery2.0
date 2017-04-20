#!/usr/bin/python
# -*- coding: utf-8 -*-


class DictHelper(object):
    @staticmethod
    def increase_dic_key(_dict, key):
        _dict[key] = 1 if key not in _dict else _dict[key] + 1

    @staticmethod
    def append_dic_key(_dict, key, value):
        if key in _dict.keys():
            _dict[key].append(value)
        else:
            _dict[key] = [value]