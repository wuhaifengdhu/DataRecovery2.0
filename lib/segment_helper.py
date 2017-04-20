#!/usr/bin/python
# -*- coding: utf-8 -*-
import zh_segment
from subprocess import call


class SegmentHelper(object):
    def __init__(self, excel_file, dict_file):
        self.excel_file = excel_file
        self.dict_file = dict_file
        self.user_dict = None

    @staticmethod
    def generate_user_dict(excel_name, dict_output):
        """
        Read excel file and generate dict file
        :param excel_name:  excel file name, currently only support xls file
        :param dict_output:  dict output
        :return: None
        """
        # call(['java', '-jar', 'problems.jar', excel_name, dict_output])
        call(['java', '-jar', 'dic_generate.jar', excel_name, dict_output])

    def segment(self, words, probability=0.2):
        if self.user_dict is None:
            SegmentHelper.generate_user_dict(self.excel_file, self.dict_file)
            self.user_dict = zh_segment.parse_file(self.dict_file)
            # print self.user_dict
        return zh_segment.segment_phrase(words, self.user_dict, probability)


if __name__ == '__main__':
    SegmentHelper.generate_user_dict("Input/train.xls", "zh.dic")
    seg = SegmentHelper("Input/train.xls", "zh.dic")
    print seg.segment(u"ÅÅÅbc 1235 abcd")
    origin_str = u"ÅÅÅbc 1235 abcd"
    print unicode(origin_str)


    # seg.user_dict = zh_segment.parse_file(seg.dict_file)
    # print zh_segment.segment_phrase("Abigai ABC", seg.user_dict, 0.001)
    # print seg.segment("4 30000 30000",0.1)



