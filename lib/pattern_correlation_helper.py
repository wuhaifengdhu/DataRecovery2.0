#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from excel_helper import ExcelHelper
from dict_helper import DictHelper
from pattern_helper import PatternHelper
from store_helper import StoreHelper
import time


class PatternCorrelationHelper(object):
    def __init__(self, excel_name):
        self.excel_name = excel_name
        self.header, self.raw_data = ExcelHelper.read_excel(self.excel_name)
        self.row_number, self.column_number = self.raw_data.shape
        self.column_pre_patterns = [[] for i in range(self.column_number)]
        self.column_end_patterns = [[] for i in range(self.column_number)]
        self.column_big_pattern = [[] for i in range(self.column_number)]
        self.cell_pre_patterns = [[[] for j in range(self.column_number)] for i in range(self.row_number)]
        self.cell_end_patterns = [[[] for j in range(self.column_number)] for i in range(self.row_number)]
        # use dic {pattern1: pattern2} to represent when pattern1 show in column i, column j should be with pattern2
        self.pre_pattern_relation = [[{} for j in range(self.column_number)] for i in range(self.column_number)]
        self.end_pattern_relation = [[{} for j in range(self.column_number)] for i in range(self.column_number)]

    #找出每一列的两种pattern: 前面一样，后面一样，分别存到self.column_pre_patterns和self.column_end_patterns中，
    # 给的筛选阈值为5
    # find two pattern for each column: pre , end. record in self.column_pre_patterns and
    # self.column_end_patterns, given thredshold 5
    def find_pattern(self):
        for column in range(self.column_number):
            self.column_pre_patterns[column], self.column_end_patterns[column] = self._find(column, 10)

    def _find(self, column, threshold):
        # 记录所有可能出现的feature,以供后边统计字典中该feature出现的次数
        # find all the feature , prepare for calculating the count that the feature appears
        column_list = self.raw_data[:, column]
        pre_dict = {}
        end_dict = {}
        start = time.clock()
        for i in range(self.row_number):
            for j in range(i+1, self.row_number):
                pre_pattern = PatternHelper.find_pre_common_str(column_list[i], column_list[j])
                end_pattern = PatternHelper.find_end_common_str(column_list[i], column_list[j])
                if pre_pattern != '':
                    DictHelper.increase_dic_key(pre_dict, pre_pattern)
                    self.cell_pre_patterns[i][column].append(pre_pattern)
                    self.cell_pre_patterns[j][column].append(pre_pattern)
                if end_pattern != '':
                    DictHelper.increase_dic_key(end_dict, end_pattern)
                    self.cell_end_patterns[i][column].append(end_pattern)
                    self.cell_end_patterns[j][column].append(end_pattern)
        print("find1 : {0}".format(time.clock() - start))

        pre_list = [key for key, value in pre_dict.items() if value > threshold]
        end_list = [key for key, value in end_dict.items() if value > threshold]
        return pre_list, end_list

    def find_pattern_correlation(self, threshold=3):
        # step 1. Remove cell patterns not in column pattern
        for row in range(self.row_number):
            for column in range(self.column_number):
                self.cell_pre_patterns[row][column] = list(set(self.cell_pre_patterns[row][column])
                                                           .intersection(self.column_pre_patterns[column]))
                self.cell_end_patterns[row][column] = list(set(self.cell_pre_patterns[row][column])
                                                           .intersection(self.column_end_patterns[column]))

        # step 2. Find relationship between two column
        for i in range(self.column_number):
            for j in range(i + 1, self.column_number):
                for k in range(self.row_number):
                    self._get_full_relation(i, j, k)
                self._remove_low_frequency_relationship(i, j, threshold)

    # Remove pattern appear times less than threshold
    def _remove_low_frequency_relationship(self, c1, c2, threshold):
        self.pre_pattern_relation[c1][c2] = self._clean_dict(self.pre_pattern_relation[c1][c2], threshold)
        self.pre_pattern_relation[c2][c1] = self._clean_dict(self.pre_pattern_relation[c2][c1], threshold)
        self.end_pattern_relation[c1][c2] = self._clean_dict(self.end_pattern_relation[c1][c2], threshold)
        self.end_pattern_relation[c2][c1] = self._clean_dict(self.end_pattern_relation[c2][c1], threshold)

    @staticmethod
    def _clean_dict(_dict, threshold):
        _dict = {key: value for key, value in _dict.items() if value > threshold}
        convert_dict = {}
        for key in _dict.keys():
            key_value = key.split("|")
            if len(key_value) == 2:
                convert_dict[key_value[0]] = key_value[1]
            else:
                print ("Error when split %s" % key)
        return convert_dict

    # Get relation ship between column1 and column2 on certain row
    def _get_full_relation(self, column1, column2, row):
        # for pre pattern
        cell1_patterns = self.cell_pre_patterns[row][column1]
        cell2_patterns = self.cell_pre_patterns[row][column2]
        for pattern1 in cell1_patterns:
            for pattern2 in cell2_patterns:
                DictHelper.increase_dic_key(self.pre_pattern_relation[column1][column2], pattern1 + "|" + pattern2)
                DictHelper.increase_dic_key(self.pre_pattern_relation[column2][column1], pattern2 + "|" + pattern1)

        # for end pattern
        cell1_patterns = self.cell_end_patterns[row][column1]
        cell2_patterns = self.cell_end_patterns[row][column2]
        for pattern1 in cell1_patterns:
            for pattern2 in cell2_patterns:
                DictHelper.increase_dic_key(self.end_pattern_relation[column1][column2], pattern1 + "|" + pattern2)
                DictHelper.increase_dic_key(self.end_pattern_relation[column2][column1], pattern2 + "|" + pattern1)

    def build_pattern_relationship(self):
        start = time.clock()
        self.find_pattern()
        print ("find_pattern : {0}".format(time.clock() - start))

        start = time.clock()
        self.find_pattern_correlation()
        print ("correlation : {0}".format(time.clock() - start))

    def save(self, file_name="pattern_relationship.dat"):
        StoreHelper.store_data(self, file_name)

    @staticmethod
    def build_from_file(file_name="pattern_relationship.dat"):
        return StoreHelper.load_data(file_name)

    @staticmethod
    def _big_pattern(data_list):
        big_pattern = set()
        for item in data_list:
            _pattern = PatternHelper.find_first_word_length(item)
            if _pattern is not None:
                big_pattern.add(_pattern)
        big_pattern = list(big_pattern)
        min_key = min(big_pattern)
        max_key = max(big_pattern)
        if min_key[0] != max_key[0]:
            return None
        else:
            return [min_key, max_key]

    # find the big pattern that suits each item in the column, I choose the length of the first word
    def build_big_pattern(self):
        for i in range(self.column_number):
            self.column_big_pattern[i] = self._big_pattern(self.raw_data[:, i])

    def match_big_pattern(self, pattern, column):
        if self.column_big_pattern[column] is not None:
            min_pattern, max_pattern = self.column_big_pattern[column]
            if min_pattern < pattern < max_pattern:
                return True
        return False

    def get_small_pattern(self, content, column):
        max_length_pre_candidate = ""
        max_length_end_candidate = ""
        for pattern in self.column_pre_patterns[column]:
            pre_pattern = PatternHelper.find_pre_common_str(pattern, content)
            if pre_pattern == pattern and len(pattern) > len(max_length_pre_candidate):
                max_length_pre_candidate = pattern
        for pattern in self.column_end_patterns[column]:
            end_pattern = PatternHelper.find_end_common_str(pattern, content)
            if end_pattern == pattern and len(pattern) > len(max_length_end_candidate):
                max_length_end_candidate = pattern
        return max_length_pre_candidate, max_length_end_candidate

    def vote_for_column(self, c_column, c_small_pattern, j_column, j_small_pattern):
        if j_small_pattern[0] in self.pre_pattern_relation[j_column][c_column] and c_small_pattern[0] == self.pre_pattern_relation[j_column][c_column][j_small_pattern[0]]:
            return True
        if j_small_pattern[1] in self.end_pattern_relation[j_column][c_column] and c_small_pattern[1] == self.end_pattern_relation[j_column][c_column][j_small_pattern[1]]:
            return True
        return False




if __name__ == "__main__":
    train = PatternCorrelationHelper("Input1/train.xls")
    train.build_pattern_relationship()
    train.build_big_pattern()
    train.save()

