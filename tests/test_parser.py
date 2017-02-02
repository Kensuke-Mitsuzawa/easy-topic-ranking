#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

from easyTopicClustering.parser import Parser
from easyTopicClustering.models.params import Params
from pandas import DataFrame
import unittest


class TestParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_parser_csvfile(self):

        inputFilePath = 'resources/inputSample.csv'
        projectName = 'example'

        pathConfigFile = 'resources/ldaConfig.ini'
        pathStopWords = 'resources/stopWord.csv'

        docker_sudo = False
        dockerID = 'aa2685b94082'

        pathNeologd = "/usr/local/lib/mecab/dic/mecab-ipadic-neologd/"
        pathUserDict = ""


        param_object = Params(projectName=projectName,
                              lang='ja',
                              inputFile=inputFilePath,
                              targetColumnName='contents',
                              indexColumnName='docIndex',
                              encoding='utf-8',
                              sheetName='',
                              min=2,
                              max=5,
                              model='lda',
                              nSentence=2,
                              nTopWords=15,
                              pathNeologdDict=pathNeologd,
                              pathUserDict=pathUserDict,
                              osType='mac',
                              dockerId=dockerID,
                              dockerSudo=docker_sudo,
                              mailTo='',
                              mailFrom='',
                              subject='',
                              workingDir='../easyTopicClustering/tmpDir',
                              pathParamConfig=pathConfigFile,
                              pathStopWord=pathStopWords)


        file_parser = Parser(param_object)
        targetSentenceFrame = file_parser.load_data()
        assert isinstance(targetSentenceFrame, DataFrame)


    def test_parser_csvfile(self):

        inputFilePath = 'resources/inputSample.xlsx'
        projectName = 'example'

        pathConfigFile = 'resources/ldaConfig.ini'
        pathStopWords = 'resources/stopWord.csv'

        docker_sudo = False
        dockerID = 'aa2685b94082'

        pathNeologd = "/usr/local/lib/mecab/dic/mecab-ipadic-neologd/"
        pathUserDict = ""


        param_object = Params(projectName=projectName,
                              lang='ja',
                              inputFile=inputFilePath,
                              targetColumnName='contents',
                              indexColumnName='docIndex',
                              encoding='utf-8',
                              sheetName='Sheet1',
                              min=2,
                              max=5,
                              model='lda',
                              nSentence=2,
                              nTopWords=15,
                              pathNeologdDict=pathNeologd,
                              pathUserDict=pathUserDict,
                              osType='mac',
                              dockerId=dockerID,
                              dockerSudo=docker_sudo,
                              mailTo='',
                              mailFrom='',
                              subject='',
                              workingDir='easyTopicClustering/tmpDir',
                              pathParamConfig=pathConfigFile,
                              pathStopWord=pathStopWords)


        file_parser = Parser(param_object)
        targetSentenceFrame = file_parser.load_data()
        assert isinstance(targetSentenceFrame, DataFrame)


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestParser))

    return suite