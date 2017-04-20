#!/usr/bin/python
# -*- coding: utf-8 -*-

from segment_helper import SegmentHelper
from excel_helper import ExcelHelper
from pattern_helper import PatternHelper
import unicodedata
import copy
import time
from pattern_correlation_helper import PatternCorrelationHelper
import re
class Step1(object):
    def __init__(self, excel_name_training, excel_name_test,  dict_file="zh.dic"):
        self.excel_name_training = excel_name_training
        self.excel_name_test = excel_name_test
        self.dict_file = dict_file
        self.header_training, self.train_data = ExcelHelper.read_excel(self.excel_name_training)
        self.header_test,self.test_data = ExcelHelper.read_excel(self.excel_name_test)
        self.row_number_training, self.column_number_training = self.train_data.shape
        self.row_number_test, self.column_number_test = self.test_data.shape
        self.segment = SegmentHelper(self.excel_name_training, self.dict_file)  # generate dictionary for training data


    def _big_pattern(self,list):
        strtemp = ""
        big_pattern = {}
        for item in list:
            strtemp = PatternHelper.find_first_word_length(item)
            if strtemp != 0:
                if (strtemp not in big_pattern.keys()):
                    big_pattern[strtemp] = 1
                else:
                    big_pattern[strtemp] += 1
        min_key = min(item for item in big_pattern.keys())
        max_key = max(item for item in big_pattern.keys())
        # print min_key,max_key
        if min_key[0] != max_key[0]:
            return None
        else:
            return min_key, max_key


    # find the big pattern that suits each item in the column, I choose the length of the first word
    def _find_big_pattern(self):
        self.pattern_list = []
        for i in range(self.column_number_training):
            if self._big_pattern(self.train_data[:,i]) != None:
                min_key, max_key = self._big_pattern(self.train_data[:, i])
                self.pattern_list.append([min_key, max_key])
            else:
                self.pattern_list.append([None])

        # print self.pattern_list


# get the test data, then splite it into phrases , return the result
    def _get_test_str_list(self):
        tempstr = ""
        self.test_str_list = []
        for i in range(self.row_number_test):
            row_list = self.test_data[i,:]
            # print "row_list = {0}".format(row_list)
            tempstr = ""
            for item in row_list:
                tempstr += str(item)+" "
            self.test_str_list.append(self.segment.segment(unicode(tempstr)))

        return self.test_str_list



    def get_dic(self,one,two,three):
        dic = {}
        for i in range(len(self.train_data)):
            # print "length = {0}".format(self.train_data[i])
            key1 = unicode(self.train_data[i][one])+","+unicode(self.train_data[i][two])+","
            key2 = unicode(self.train_data[i][two]) +"," + unicode(self.train_data[i][one]) +","
            if key1 not in dic.keys():
                dic[key1] = [self.train_data[i][three]]
            elif self.train_data[i][three] not in dic[key1]:
                dic[key1].append(self.train_data[i][three])

            if key2 not in dic.keys():
                dic[key2] = [self.train_data[i][three]]
            elif self.train_data[i][three] not in dic[key2]:
                dic[key2].append(self.train_data[i][three])
        return dic

    def get_two_to_one_dic(self):
        self.onetwo_to_three_dic = {}
        self.onethree_to_two_dic = {}
        self.twothree_to_one_dic = {}

        self.onetwo_to_three_dic = self.get_dic(0,1,2)
        self.onethree_to_two_dic = self.get_dic(0,2,1)
        self.twothree_to_one_dic = self.get_dic(1,2,0)



    def recover(self):

        print "recovering now, please wait ..."
        start = time.clock()
        train = PatternCorrelationHelper("Input/train.xls")
        self.correlation = train.patter_correlation()
        elapsed = (time.clock() - start)
        print("Time5555 used:", elapsed)
        # print self.correlation[1][2][0]
        # combine all the keys in the same row of self.correlation, prepare for find_pattern
        self.pattern_key = [[] for i in range(self.column_number_training)]  # record the whole keys for one column
        keys = []
        for i in range(self.column_number_training):
            for k in range(len(self.correlation[i])):
                # print self.correlation[i][k]
                if self.correlation[i][k] != []:
                    keys = list(set(keys + self.correlation[i][k][0].keys()))

            self.pattern_key[i] = keys
            keys = []


        self.recover_data = [([""]*3) for i in range(len(self.test_str_list))]
        strtemp = ""
        dic_item_to_column = {}   # recored the row number of the column
        dic_column_to_item = {}
        flag = [False] * self.column_number_training
        # for i in range(len(self.test_str_list)):
        #     print self.test_str_list[i]


        for i in range(len(self.test_str_list)):
            # print "test_str_list[i] = {0}".format(self.test_str_list[i])
            for item in self.test_str_list[i]:
                if not item:
                    continue
                else:
                    strtemp = PatternHelper.find_first_word_length(str(item))
                    for k in range(len(self.pattern_list)):
                        if self.pattern_list[k][0] != None and strtemp >= self.pattern_list[k][0] and strtemp <= self.pattern_list[k][1]:
                            if item in self.train_data[:, k]:
                                # give the value to dic_colum_to_item, and dic_item_to_column
                                if k not in dic_column_to_item.keys():
                                    dic_column_to_item[k] = [item]
                                elif item not in dic_column_to_item[k]:
                                    dic_column_to_item[k].append(item)

                                if item not in dic_item_to_column.keys():
                                    dic_item_to_column[item] = [k]
                                elif k not in dic_item_to_column[item]:
                                    dic_item_to_column[item].append(k)
                            # print dic_column_to_item
                            # print dic_item_to_column


            #now control dic_column_to_item and dic_item_to_colunm
            for key1 in dic_item_to_column:
                for key2 in dic_column_to_item:
                    if len(dic_item_to_column[key1]) == 1 and len(dic_column_to_item[key2]) == 1 and dic_item_to_column[key1][0] == key2 and dic_column_to_item[key2][0] == key1:     # 1 column to 1 item
                        # print "key1 = {0}, key2 = {1}".format(key1,key2)
                        self.recover_data[i][key2] = key1
                        flag[key2] = True

            # find by pattern-correlation
            temppattern = [[] for t in range(len(flag))]
            pattern_list = [[] for t in range(len(flag))]
            for ii in range(len(flag)):
                if ii in dic_column_to_item.keys():
                    pattern_list[ii] = self.find_pattern(self,dic_column_to_item[ii],self.pattern_key[ii])
            # print pattern_list

            # compare each two pattern, if mathes, find it in the training data
            for ii in range(len(flag)):
                for jj in range(len(flag)):
                    if ii == jj:
                        continue
                    else:
                        pattern1 = pattern_list[ii]
                        pattern2 = pattern_list[jj]

                        for p1 in range(len(pattern1)):
                            for pp1 in range(len(pattern1[p1])):
                                if self.correlation[ii][jj] != [] and pattern1[p1][pp1] in self.correlation[ii][jj][0].keys():
                                    for p2 in range(len(pattern2)):
                                        for pp2 in range(len(pattern2[p2])):
                                            # print pattern1[p1][pp1]
                                            # print self.correlation[ii][jj][0][pattern1[p1][pp1]]
                                            if pattern2[p2][pp2] in self.correlation[ii][jj][0][pattern1[p1][pp1]]:
                                                # print pattern1[p1][pp1], pattern2[p2][pp2]
                                                if Step1.search(self,ii,jj,dic_column_to_item[ii][p1],dic_column_to_item[jj][p2]) == True:
                                                    self.recover_data[i][ii] = dic_column_to_item[ii][p1]
                                                    self.recover_data[i][jj] = dic_column_to_item[jj][p2]
                                                    flag[ii] = True
                                                    flag[jj] = True
            # # fill in the blank cells
            if flag.count(False) == 1:
                index = flag.index(False)
                temp_key = ""
                for flag_index in range(len(flag)):
                    if flag[flag_index] == True:
                        temp_key += unicode(self.recover_data[i][flag_index]) + ","
                if temp_key in self.onetwo_to_three_dic.keys():
                    value = self.onetwo_to_three_dic[temp_key]
                if temp_key in self.onethree_to_two_dic.keys():
                    value = self.onethree_to_two_dic[temp_key]
                if temp_key in self.twothree_to_one_dic.keys():
                    value = self.twothree_to_one_dic[temp_key]
                self.recover_data[i][index] = value


            dic_item_to_column = {}
            dic_column_to_item = {}
            flag = [False] * self.column_number_training


        return self.recover_data

# find pre and end pattern for the candidate
    @staticmethod
    def find_pattern(self,list,keys):
        pattern_list = [[] for i in range(len(list))]
        pattern_list_dic = {}
        # print pattern_list
        # keys = correlation_dic.keys()  # find all the keys for this column
        for i in range(len(list)):
            for key in keys:
                tempkey = key.split('_')
                pattern_temp = ""
                if tempkey[0] == 'P':
                    pattern_temp = PatternHelper.find_pre_common_str(tempkey[1],list[i])
                    if pattern_temp:
                        pattern_list[i].append(unicode('P_'+pattern_temp))
                elif tempkey[0] == 'E':
                    pattern_temp = PatternHelper.find_end_common_str(tempkey[1],list[i])
                    if pattern_temp:
                        pattern_list[i].append(unicode('E_'+pattern_temp))
        # print pattern_list
        return pattern_list

    @staticmethod
    def search(self,i,j,str1,str2):
        for k in range(self.row_number_training):
            if self.train_data[k][i] == str1 and self.train_data[k][j] == str2:
                return True
        return False





# training data need to be xls
if __name__ == '__main__':
    start = time.clock()
    step = Step1("Input/train.xls","Input/test1.xls","zh.dic")
    elapsed = (time.clock() - start)
    print("Time1 used:", elapsed)
    start = time.clock()
    step.segment.generate_user_dict("Input/train.xls","zh.dic")
    elapsed = (time.clock() - start)
    print("Time2 used:", elapsed)
    start = time.clock()
    step._find_big_pattern()
    elapsed = (time.clock() - start)
    print("Time3 used:", elapsed)
    start = time.clock()

    step.test_str_list = step._get_test_str_list()
    elapsed = (time.clock() - start)
    print("Time4 used:", elapsed)
    start = time.clock()
    step.get_two_to_one_dic()
    elapsed = (time.clock() - start)
    print("Time5 used:", elapsed)
    start = time.clock()
    data =  step.recover()
    elapsed = (time.clock() - start)
    print("Time6 used:", elapsed)
    start = time.clock()
    ExcelHelper.write_excel("Output/reover1.xlsx",data,"sheet1",step.header_training)
    elapsed = (time.clock() - start)
    print("Time7 used:", elapsed)
    start = time.clock()




















