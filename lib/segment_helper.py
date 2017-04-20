#!/usr/bin/python
# -*- coding: utf-8 -*-
from subprocess import call
import re
import io


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
            self.user_dict = SegmentHelper.parse_file(self.dict_file)
            # print self.user_dict
        return SegmentHelper._segment_phrase(words, self.user_dict, probability)

    @staticmethod
    def parse_file(filename):
        "Read `filename` and parse tab-separated file of (word, count) pairs."
        with io.open(filename, encoding='iso-8859-1') as reader:
            lines = (line.split('\t') for line in reader)
            return dict((word.lower(), float(number)) for word, number in lines)

    @staticmethod
    def _segment_text(text):
        """Return a list of words that is the best segmentation of `text`."""
        result = []
        for x in re.split(';|,| ', text):
            # Deal with condition digital and letter mix
            y_list = [y for y in re.split('([\d|-|%|+]+)', x) if len(y) > 0]
            result.extend(y_list)
        return result

    @staticmethod
    def _segment_phrase(text, probability_dic, rate):
        text = unicode(text)
        result = SegmentHelper._segment_text(text)
        result.append('')
        phrases = []
        phrase = ''
        for i in range(len(result) - 1):
            pair = '%s %s' % (result[i].lower(), result[i + 1].lower())
            phrase += ' ' + result[i] if len(phrase) > 0 else result[i]
            if pair not in probability_dic.keys() or probability_dic[pair] < rate:
                phrases.append(unicode(phrase))
                phrase = ''
        if len(phrase) > 0:
            phrases.append(unicode(phrase))
        return phrases


if __name__ == '__main__':
    SegmentHelper.generate_user_dict("Input/train.xls", "zh.dic")
    seg = SegmentHelper("Input/train.xls", "zh.dic")
    print seg.segment(u"ÅÅÅbc 1235 abcd")
    origin_str = u"ÅÅÅbc 1235 abcd"
    print unicode(origin_str)


    # seg.user_dict = zh_segment.parse_file(seg.dict_file)
    # print zh_segment.segment_phrase("Abigai ABC", seg.user_dict, 0.001)
    # print seg.segment("4 30000 30000",0.1)



