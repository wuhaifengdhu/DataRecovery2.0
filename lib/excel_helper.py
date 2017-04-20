#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import pandas as pd
import xlwt as excel
import unicodedata


class ExcelHelper(object):
    @staticmethod
    def read_excel(excel_file):
        excel_data = pd.read_excel(excel_file)
        excel_data.fillna('', inplace=True)
        return excel_data.columns.tolist(), excel_data.values

    @staticmethod
    def write_excel(excel_file, data_array, sheet_name="data", header=None):
        book = excel.Workbook()
        sheet = book.add_sheet(sheet_name)
        # row,column = data_array.shape
        row = len(data_array)
        column = len(data_array[0])

        # Write header to the first line if header exist
        if header:
            for i in range(len(header)):
                sheet.write(0,i,header[i])

        # Write body with render color
        for i in range(row):
            for j in range(column):
                sheet.write(i + 1, j, unicode(data_array[i][j]))

        book.save(excel_file)

    @staticmethod
    def change_unicode_to_str(self, item):
        try:
            item = str(item).lower()
        except UnicodeEncodeError:
            item = unicodedata.normalize('NFKD', item).encode('ascii', 'ignore')
        return item



if __name__ == '__main__':
    _header, _data = ExcelHelper.read_excel('user.xls')
    # data.shape返回表格内容的行列数（不包括表头）
    _row, _col = _data.shape
    #mask变成了一个二维的列表
    _mask = [[] for i in range(_col)]


    for i in range(_col):
        _mask[i].extend([1 if _data[r, i] < 0 else 0 for r in range(_row)])
    _color_dic = {1: "red"}
    ExcelHelper.write_excel("user_render.xls", _data, "data", _header, _mask, _color_dic)
