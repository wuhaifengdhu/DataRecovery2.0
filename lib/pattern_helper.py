#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import unicodedata


class PatternHelper(object):
    # Return common prefix if exist else ''
    @staticmethod
    def find_pre_common_str(str1, str2):
        # str1 = unicode(str1)
        # str2 = unicode(str2)
        for i in range(min(len(str1), len(str2))):
            if str1[i] != str2[i]:
                return str1[: i]
        return str1 if len(str1) < len(str2) else str2

    # Return common suffix if exist else ''
    @staticmethod
    def find_end_common_str(str1, str2):
        return PatternHelper.find_pre_common_str(str1[::-1], str2[::-1])[::-1]

    # 大pattern,找出对每列来说所有数据都符合的pattern, 数据中第一个单词：若为数字，找出数字的N+长度，若为单词，S+数字长度
    @staticmethod
    def find_first_word_length(item):
        if not item:
            return None
        else:
            str_list = unicode(item).split()
            return 'N'+str(len(str_list[0])) if PatternHelper.is_number(str_list[0]) else 'S' + str(len(str_list[0]))

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False


if __name__ == '__main__':
    pattern_help = PatternHelper()
    print pattern_help.find_pre_common_str("41234", "1234")
    # print pattern_help.find_end_common_str("1234","1234")

    # excel_data.fillna('',inplace=True)
    # item = pattern_help.change_unicode_to_str(excel_data.values[0][0])
    # print pattern_help.find_first_word_length(item)
    # print str(excel_data.values[0]).split()
    print PatternHelper.find_pre_common_str("àðcd", "àðfg")
    # print PatternHelper.find_first_word_length(123456782345785325)






