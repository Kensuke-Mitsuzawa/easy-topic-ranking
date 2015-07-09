#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'


class Params(object):

    def __init__(self, targetColumnName, indexColumnName, encoding, sheetName, min, max, model, nSentence, pathNeologdDict, osType):
        self.file_param = FileParams(targetColumnName, indexColumnName, encoding, sheetName)
        self.topic_param = TopicParams(min, max, model)
        self.sent_extract = SentExtractParams(nSentence, pathNeologdDict, osType)

class FileParams(object):

    def __init__(self, targetColumnName, indexColumnName, encoding, sheetName):
        self.targetColumnName = targetColumnName
        self.indexColumnName = indexColumnName
        self.encoding = encoding
        self.sheetName = sheetName


class TopicParams(object):

    def __init__(self, min, max, model):
        self.min_topic = min
        self.max_topic = max
        self.model = model


class SentExtractParams(object):

    def __init__(self, nSentence, pathNeologdDict, osType):
        self.nSentence = nSentence
        self.pathNeologdDict = pathNeologdDict
        self.osType = osType


