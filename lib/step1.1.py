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
#########################################################################################################
        # #è¿ä¸¤ä¸ªforå¾ªç¯ï¼å°train_dataåtest_dataä»unicodeç±»åè½¬åä¸ºstrç±»åï¼ä»¥ä¾¿åé¢å¤ç
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
        if min_key[0] != max_key[0]:   #è¥å­å¸éé¢keyçæå¤§å¼æå°å¼å¼å¤´ç¬¬ä¸ä¸ªå­æ¯ä¸ä¸æ ·ï¼è¯´æä¸è½ç¾åç¾ä¿è¯è¿åçå¼å¤´åè¯æ¯åè¯æèå­ç¬¦ä¸²
            return None
        else:
            return min_key, max_key


    # æ¾å°æ¯ä¸åçå¤§patternï¼æå¤§ï¼æå°ï¼ï¼è¿åpatternçlist
    def _find_big_pattern(self):
        self.pattern_list = []   #å­å¨å¤§æ¯åçå¤§patternï¼åæ¬æå¤§å¼åæå°å¼ï¼
        for i in range(self.column_number_training):
            if self._big_pattern(self.train_data[:,i]) != None:
                min_key, max_key = self._big_pattern(self.train_data[:, i])
                self.pattern_list.append([min_key, max_key])
            else:
                self.pattern_list.append([None])

        print self.pattern_list

#å°test dataéçæ¯ä¸è¡æ°æ®åè¿è¡æ¼æ¥ï¼ååè¯ï¼è¿ååè¯åæ´ä¸ªææ¬çlist
    def _get_test_str_list(self):
        tempstr = ""
        self.test_str_list = []
        for i in range(self.row_number_test):  #éåæ¯ä¸è¡
            row_list = self.test_data[i,:]
            # print "row_list = {0}".format(row_list)
            tempstr = ""
            for item in row_list:
                tempstr += str(item)+" "
            self.test_str_list.append(self.segment.segment(unicode(tempstr)))


        # print "test: {0}".format(self.test_str_list)
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

        # print "1: {0}".format(self.onetwo_to_three_dic)
        # print "2 : {0}".format(self.onethree_to_two_dic)
        # print "3: {0}".format(self.twothree_to_one_dic)





    def recover(self):
        self.recover_data = [([""]*self.column_number_training) for i in range(len(self.test_str_list))]
        strtemp = ""
        dic_candidate = {}
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
                                elif item not in dic_candidate[k]:
                                    dic_candidate[k].append(item)

            # print dic_candidate
            #################################################################################
            flag = [False] * self.column_number_training
            while True:
                temp_dic = copy.deepcopy(dic_candidate)

                for key in dic_candidate.keys():
                    if (len(dic_candidate[key]) == 1 and flag[key] == False):
                        temp = dic_candidate[key][0]
                        self.recover_data[i][key] = temp    # may cause some mistake
                        flag[key] = True
                        for r in dic_candidate.keys():
                            if temp in dic_candidate[r]:
                                dic_candidate[r].remove(temp)
                if temp_dic == dic_candidate:
                    index_true_dic = {}
                    index_false_dic = {}
                    # print "temp_dic = {0}".format(temp_dic)
                    #get the column that has more than one candicate
                    for number in range(len(flag)):
                        if flag[number] == True:
                            index_true_dic[number] = self.train_data[i, number]
                        elif number in dic_candidate.keys() and dic_candidate[number] :
                            index_false_dic[number] = dic_candidate[number]

                    # print "index_true: {0}".format(index_true_dic)
                    # print "index_false: {0}".format(index_false_dic)

                    # fill in the blank cells
                    index = [0, 1, 2]
                    tt = copy.deepcopy(index)
                    fal_list = []
                    for x in index:
                        if x not in index_true_dic.keys():
                            fal_list.append(x)
                            tt.remove(x)

                    temp_key = ""
                    # print "tt = {0}".format(tt)
                    # print "fal_list = {0}".format(fal_list)
                    for x in tt:
                        temp_key += self.recover_data[i][x] + ","
                    value = ""
                    # print "temp_key = %s"%temp_key
                    # print "len = %d"%len(tt)
                    if len(tt) == 2:
                        if temp_key in self.onetwo_to_three_dic.keys():
                            value = self.onetwo_to_three_dic[temp_key]
                        if temp_key in self.onethree_to_two_dic.keys():
                            value = self.onethree_to_two_dic[temp_key]
                        if temp_key in self.twothree_to_one_dic.keys():
                            value = self.twothree_to_one_dic[temp_key]

                    # print "value = %s"%value
                    if len(fal_list) == 1:
                        self.recover_data[i][fal_list[0]] = value

                    break

            dic_candidate = {}



        return self.recover_data


# training data need to be xls
if __name__ == '__main__':
    start = time.clock()
    step = Step1("Input/train.xls","Input/test1.xls","zh.dic")
    step.segment.generate_user_dict("Input/train.xls","zh.dic")
    step._find_big_pattern()
    step.test_str_list = step._get_test_str_list()
    step.get_two_to_one_dic()
    data =  step.recover()
    ExcelHelper.write_excel("Output/reover1.xlsx",data,"sheet1",step.header_training)
    print "time cost: {0}".format(time.clock() - start)















