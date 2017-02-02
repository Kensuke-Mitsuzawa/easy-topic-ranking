#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

import pandas
import os
import sys
from easyTopicClustering.models.params import *


class Parser(object):
    def __init__(self, params_object):
        self.params = params_object


    def _format(self):
        content_header = self.params.file_param.targetColumnName
        id_header = self.params.file_param.indexColumnName
        targetSentenceFrame = self.inputFrame.loc[:, [content_header, id_header]]
        targetSentenceFrame.columns = ['targetColumnName', 'indexColumnName']
        targetSentenceFrame.sort_values(by='indexColumnName', ascending=True)

        self.targetSentenceFrame = targetSentenceFrame


    def _check_columns(self):
        assert self.params.file_param.targetColumnName in list(self.inputFrame.columns.values)
        assert self.params.file_param.indexColumnName in list(self.inputFrame.columns.values)


    def load_data(self):

        filePath = self.params.file_param.filePath
        if self.params.file_param.mode == 'csv':
            self.inputFrame = pandas.read_csv(filePath, encoding=self.params.file_param.encoding, header=0, sep=',')
            self._check_columns()
            self._format()
            return self.targetSentenceFrame
        elif self.params.file_param.mode=='excel':
            ExcelObject = pandas.ExcelFile(filePath)
            self.inputFrame = ExcelObject.parse(self.params.file_param.sheetName)
            self._check_columns()
            self._format()
            return self.targetSentenceFrame