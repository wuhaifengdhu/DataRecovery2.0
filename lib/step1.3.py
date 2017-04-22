#!/usr/bin/python
# -*- coding: utf-8 -*-
from segment_helper import SegmentHelper
from excel_helper import ExcelHelper
from pattern_helper import PatternHelper
from dict_helper import DictHelper
import copy
import time
from pattern_correlation_helper import PatternCorrelationHelper


class Step1(object):
    def __init__(self, excel_name_training, excel_name_test, dict_file="zh.dic"):
        self.excel_name_training = excel_name_training
        self.excel_name_test = excel_name_test
        self.dict_file = dict_file
        self.header_training, self.train_data = ExcelHelper.read_excel(self.excel_name_training)
        self.header_test, self.test_data = ExcelHelper.read_excel(self.excel_name_test)
        self.row_number_training, self.column_number_training = self.train_data.shape
        self.row_number_test, self.column_number_test = self.test_data.shape
        self.segment = SegmentHelper(self.excel_name_training, self.dict_file)  # generate dictionary for training data
        self.test_str_list = [0 for i in range(self.row_number_test)]
        self.test_repair_data = copy.deepcopy(self.test_data)
        self.train = None

    # get the test data, then split it into phrases , return the result
    def get_test_str_list(self):
        for row in range(self.row_number_test):
            temp_str = " ".join([unicode(item) for item in self.test_data[row, :]])
            self.test_str_list[row] = self.segment.segment(unicode(temp_str))

    def training(self, save_result=True, save_file="pattern_relationship.dat", recover_file=None):
        if self.train is not None:
            return
        if recover_file is not None:
            self.train = PatternCorrelationHelper.build_from_file(recover_file)
            return
        self.train = PatternCorrelationHelper(self.excel_name_training)
        self.train.build_big_pattern()
        self.train.build_pattern_relationship()
        if save_result:
            self.train.save(save_file)

    def recover(self):
        for row in range(self.row_number_test):
            self.recover_row(row)

    def recover_row(self, row):
        # store all candidate for each column
        recover_list = [[] for i in range(self.column_number_test)]
        # Store relationship { segmented text --> big pattern }
        big_pattern_dict = {text: (PatternHelper.find_first_word_length(text), PatternHelper.find_last_word_length(text)
                                   ) for text in self.test_str_list[row]}
        # store judge's small pattern (judge is the one only one candidate in a excel cell)
        small_pattern_list = [[] for i in range(self.column_number_test)]

        # step 1. Get all element for match big pattern
        for i in range(self.column_number_test):
            for key, value in big_pattern_dict.items():
                if self.train.match_big_pattern(value, i):
                    recover_list[i].append(key)


        # step 2. Check for candidate more than one
        # for only one candidate cell can be a judge vote for other cell
        # for zero candidate cell, will ignore
        while True:
            old_recover_list = copy.deepcopy(recover_list)

            # update judge small pattern
            for column in range(self.column_number_test):
                if len(recover_list[column]) == 1 and len(small_pattern_list[column]) == 0:
                    Step1.column_choose_decided(recover_list, column)

            # vote for 2 more candidate
            # for column in range(self.column_number_test):
            #     if len(recover_list[column]) > 1:
            #         score_dict = self.score_column_candidate(column, recover_list, small_pattern_list)
            #         if len(score_dict) == 0:
            #             continue
            #         max_score = max(score_dict.values())
            #         recover_list[column] = []
            #         for candidate, score in score_dict.items():
            #             if score == max_score:
            #                 recover_list[column].append(candidate)

            # break for no further change
            if old_recover_list == recover_list:
                break
        # step 3. recover data
        for column in range(self.column_number_test):
            self.test_repair_data[row][column] = recover_list[column][0] if len(recover_list[column]) > 0 else ''

    def score_column_candidate(self, column, recover_list, small_pattern_list):
        score_dict = {}
        for candidate in recover_list[column]:
            candidate_small_pattern = self.train.get_small_pattern(candidate, column)
            for j in range(self.column_number_test):
                if len(recover_list[j]) == 1 and self.train.vote_for_column(column, candidate_small_pattern, j,
                                                                            small_pattern_list[j]):  # can be a judge
                    DictHelper.increase_dic_key(score_dict, candidate)
        return score_dict

    @staticmethod
    def column_choose_decided(recover_list, column):
        for i in range(len(recover_list)):
            if i != column and recover_list[column][0] in recover_list[i] and len(recover_list[i]) > 1:
                recover_list[i].remove(recover_list[column][0])


# training data need to be xls
if __name__ == '__main__':
    start = time.clock()
    # step 1. Init Step class
    step = Step1("Input1/train.xls", "Input1/test1.xls", "zh.dic")
    elapsed = (time.clock() - start)
    print("Time1 used:", elapsed)
    start = time.clock()
    # step 2. General words dic from train.xls
    step.segment.generate_user_dict("Input1/train.xls", "zh.dic")
    elapsed = (time.clock() - start)
    print("Time2 used:", elapsed)
    start = time.clock()

    # step 3. split test into phrase
    step.get_test_str_list()
    elapsed = (time.clock() - start)
    print("Time3 used:", elapsed)

    # step 4. Generic pattern relationship
    start = time.clock()
    # step.training(recover_file="pattern_relationship.dat")
    step.training()
    print("Time4 used:", (time.clock() - start))

    # step 5. Recover
    start = time.clock()
    step.recover()
    elapsed = (time.clock() - start)
    print("Time5 used:", elapsed)

    # step 6. write to excel
    start = time.clock()
    ExcelHelper.write_excel("Output/reover1.xls", step.test_repair_data, "sheet1", step.header_training)
    elapsed = (time.clock() - start)
    print("Time6 used:", elapsed)
