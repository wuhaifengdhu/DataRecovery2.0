#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from excel_helper import ExcelHelper
from dict_helper import DictHelper
from pattern_helper import PatternHelper
import time


class PatternCorrelationHelper(object):
    def __init__(self, excel_name):
        self.excel_name = excel_name
        self.header, self.raw_data = ExcelHelper.read_excel(self.excel_name)
        self.row_number, self.column_number = self.raw_data.shape
        self.column_pre_patterns = [[] for i in range(self.column_number)]
        self.column_end_patterns = [[] for i in range(self.column_number)]
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
            self.column_pre_patterns[column], self.column_end_patterns[column] = self.find(column, 10)

    def find(self, column, threshold):
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

    # 生成一列的pattern_row字典和row_pattern字典
    @staticmethod
    def generate_pattern_dic(column_list, pre_pattern_list, end_pattern_list):
        dic_pattern_row = {}
        dic_row_pattern = {}

        # 存入字典时，对于pattern,若是前面相同的pattern "P"+pattern ,若是后面一样"E"+pattern
        for i in range(len(column_list)):
            for pattern in pre_pattern_list:
                if PatternHelper.find_pre_common_str(column_list[i], pattern) == pattern:
                    if "P_" + pattern not in dic_pattern_row.keys():
                        dic_pattern_row["P_" + pattern] = [i]
                    else:
                        dic_pattern_row["P_" + pattern].append(i)

                    if i not in dic_row_pattern.keys():
                        dic_row_pattern[i] = ["P_" + pattern]
                    else:
                        dic_row_pattern[i].append("P_" + pattern)

            for pattern in end_pattern_list:
                if PatternHelper.find_end_common_str(column_list[i], pattern) == pattern:
                    if "E_" + pattern not in dic_pattern_row.keys():
                        dic_pattern_row["E_" + pattern] = [i]
                    else:
                        dic_pattern_row["E_" + pattern].append(i)

                    if i not in dic_row_pattern.keys():
                        dic_row_pattern[i] = ["E_" + pattern]
                    else:
                        dic_row_pattern[i].append("E_" + pattern)
        return dic_pattern_row, dic_row_pattern

    #生成patter_row和row_pattern的字典列表，列表中共有column_number个字典，
    #generate two kinds of dic list, patter_row_dic and row_pattern_dic, there are column_number dictionary in each list
    def generate_pattern_dic_list(self):
        # step 1. Remove cell patterns not in column pattern
        for row in range(self.row_number):
            for column in range(self.column_number):
                self.cell_pre_patterns[row][column] = list(set(self.cell_pre_patterns[row][column])
                                                           .intersection(self.column_pre_patterns[column]))
                self.cell_end_patterns[row][column] = list(set(self.cell_pre_patterns[row][column])
                                                           .intersection(self.column_end_patterns[column]))

        # step 2. Generate pattern_row_dic, row_pattern_dic
        for i in range(self.column_number):
            dic1,dic2 = PatternCorrelationHelper.generate_pattern_dic(self.raw_data[:,i],self.column_pre_patterns[i],self.column_end_patterns[i])
            self.pattern_row_dic.append(dic1)
            self.row_pattern_dic.append(dic2)
        # print self.pattern_row_dic
        # print self.row_pattern_dic

     #column1和column2分别代表列标号
    def find_pattern_correlation(self, cell_dict):
        # step 1. Remove cell patterns not in column pattern
        for row in range(self.row_number):
            for column in range(self.column_number):
                self.cell_pre_patterns[row][column] = list(set(self.cell_pre_patterns[row][column])
                                                           .intersection(self.column_pre_patterns[column]))
                self.cell_end_patterns[row][column] = list(set(self.cell_pre_patterns[row][column])
                                                           .intersection(self.column_end_patterns[column]))

        # step 2. Find relationship between two column
        for i in range(self.column_number):
            for j in range(self.column_number):
                if i == j:
                    continue
                for k in range(self.row_number):
                    self.pre_pattern_relation[i][j]




    def patter_correlation(self):
        start = time.clock()
        self.find_pattern()
        print ("find_pattern : {0}".format(time.clock() - start))

        start = time.clock()
        self.generate_pattern_dic_list()
        print ('generate_pattern_dic_list : {0}'.format(time.clock() - start))

        start = time.clock()
        self.find_pattern_correlation(self.cell_pre_patterns)
        print ("correlation : {0}".format(time.clock() - start))
        return self.correlation


if __name__ == "__main__":
    train = PatternCorrelationHelper("Input/train.xls")
    train.patter_correlation()

