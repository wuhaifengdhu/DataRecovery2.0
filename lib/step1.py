#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from segment_helper import SegmentHelper
from excel_helper import ExcelHelper
from pattern_helper import PatternHelper
import unicodedata
import copy
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
#########################################################################################################
        # #这两个for循环，将train_data和test_data从unicode类型转化为str类型，以便后面处理
        # for i in range(self.column_number_training):
        #     self.train_data[:,i] = self._change_data_to_str(self.train_data[:,i])
        #
        #
        # for i in range(self.column_number_test):
        #     self.test_data[:,i] = self._change_data_to_str(self.test_data[:,i])


    def _change_data_to_str(self,list):
        for i in range(len(list)):
            list[i] = Step1.change_unicode_to_str(list[i])
        return list

    @staticmethod
    def change_unicode_to_str( item):
        try:
            item = str(item)
        except UnicodeEncodeError:
            item = unicodedata.normalize('NFKD', item).encode('ascii', 'ignore')
        return item

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
        if min_key[0] != max_key[0]:   #若字典里面key的最大值最小值开头第一个字母不一样，说明不能百分百保证这列的开头单词是单词或者字符串
            return None
        else:
            return min_key, max_key


    # 找到每一列的大pattern（最大，最小），返回pattern的list
    def _find_big_pattern(self):
        self.pattern_list = []   #存储大每列的大pattern（包括最大值和最小值）
        for i in range(self.column_number_training):
            if self._big_pattern(self.train_data[:,i]) != None:
                min_key, max_key = self._big_pattern(self.train_data[:, i])
                self.pattern_list.append([min_key, max_key])
            else:
                self.pattern_list.append([None])

        print self.pattern_list

#将test data里的每一行数据先进行拼接，再分词，返回分词后整个文本的list
    def _get_test_str_list(self):
        tempstr = ""
        self.test_str_list = []
        for i in range(self.row_number_test):  #遍历每一行
            row_list = self.test_data[i,:]
            tempstr = ""
            for item in row_list:
                tempstr += str(item)+" "

            self.test_str_list.append(self.segment.segment(unicode(tempstr)))
        print "test: {0}".format(self.test_str_list)
        return self.test_str_list

    # self.recover_data用来存放找好的数据
    def recover(self):
        self.recover_data = [([""]*3) for i in range(len(self.test_str_list))]
        strtemp = ""
        dic_candidate = {}  #key:改行的列号， value：该行中可能出现在该列的字符串
        for i in range(len(self.test_str_list)):
            for item in self.test_str_list[i]:
                if not item:
                    continue
                else:
                    strtemp = PatternHelper.find_first_word_length(str(item))
                    for k in range(len(self.pattern_list)):
                        if self.pattern_list[k][0] != None and strtemp >= self.pattern_list[k][0] and strtemp <= self.pattern_list[k][1]:
                            if item in self.train_data[:,k]:
                                if k not in dic_candidate.keys():
                                    dic_candidate[k] = [item]
                                else:
                                    dic_candidate[k].append(item)
            flag = [False]*self.column_number_training     #用来记录哪一列被填上了
            # print dic_candidate
            #################################################################################
            while True:
                temp_dic = copy.deepcopy(dic_candidate)
                for key in dic_candidate.keys():
                    if (len(dic_candidate[key]) == 1 and flag[key] == False):
                        temp = dic_candidate[key][0]
                        self.recover_data[i][key] = temp
                        flag[key] = True
                        for r in dic_candidate.keys():
                            if temp in dic_candidate[r]:
                                dic_candidate[r].remove(temp)
                if temp_dic == dic_candidate:
                    # print temp_dic
                    break
            dic_candidate = {}
        return self.recover_data


# training data need to be xls
if __name__ == '__main__':
    step = Step1("Input/train.xls","Input/test1.xls","zh.dic")
    step.segment.generate_user_dict("Input/train.xls","zh.dic")
    step._find_big_pattern()
    step.test_str_list = step._get_test_str_list()
    data =  step.recover()
    ExcelHelper.write_excel("Output/reover1.xlsx",data,"sheet1",step.header_training)

    # print unicode("ÅÅÅbc", "iso-8859-1").encode("utf-8")
    # # print repr("ÅÅÅbc")
    # print repr("ÅÅÅbc")
    # print '\xc3\x85\xc3\x85\xc3\x85bc'
    # dict = {'Name': 'Zara', 'Age': 7, 'Class': 'First'};
    # del dict['Name']
    # print dict['Name']
    print repr('\xc5\xc5\xc5bc')






