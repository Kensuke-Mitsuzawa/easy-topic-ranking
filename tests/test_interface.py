#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

from easyTopicClustering.models.params import Params
from easyTopicClustering.rankingInterface import main
from easyTopicClustering.send_email import generate_html_report
import unittest
import os
import sys


class TestCommandLineInterface(unittest.TestCase):

    def setUp(self):
        pass


    def test_params(self):

        #inputFilePath = '../resources/inputSample.csv'
        inputFilePath = '../resources/inputSample.xlsx'
        projectName = 'example'
        pathConfigFile = '../resources/ldaConfig.ini'
        pathStopWords = '../resources/stopWord.csv'
        working_dir = '../easyTopicClustering/tmpDir'

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
                              nTopWords=15,
                              pathUserDict='',
                              nSentence=2,
                              pathParamConfig=pathConfigFile,
                              pathStopWord=pathStopWords,
                              pathNeologdDict='/usr/local/bin/',
                              osType='mac', dockerId='', dockerSudo=False,
                              mailTo='', mailFrom='', subject='', pathSmtp='', workingDir=working_dir)
        isinstance(param_object, Params)

        pathOutPutJson = main(param_object)
        pathResource = os.path.abspath('../resources')

        abs_path_script = __file__
        abs_path_dir = abs_path_script.replace('tests/test_interface.py', '').replace('/c', '')

        #generate_html_report(pathScriptDir=abs_path_dir, pathToJson=pathOutPutJson, projetcName=projectName,
        #                     resourceDir=pathResource, mailFrom='', mailTo='', pathSmtp='', sendMail=False)



def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCommandLineInterface))

    return suite