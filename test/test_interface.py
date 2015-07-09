#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

from easyTopicClustering.models.params import Params
import unittest


class TestCommandLineInterface(unittest.TestCase):

    def setUp(self):
        pass


    def test_params(self):

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
                              workingDir='easyTopicClustering/tmpDir',
                              pathParamConfig=pathConfigFile,
                              pathStopWord=pathStopWords)



def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCommandLineInterface))

    return suite