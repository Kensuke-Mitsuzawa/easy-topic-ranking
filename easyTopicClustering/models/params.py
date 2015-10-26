#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

import os
import ConfigParser

class Params(object):

    def __init__(self, projectName, lang, inputFile, targetColumnName, indexColumnName, encoding, sheetName,
                 min, max, model, nSentence, nTopWords, pathUserDict, pathNeologdDict, pathParamConfig, pathStopWord, osType,
                 workingDir, dockerId='', dockerSudo=False, mailTo='', mailFrom='', subject='', pathSmtp=''):
        if not projectName == '':
            self.projectName = projectName
        else:
            raise IOError("projectName must not be blank")

        self.file_param = FileParams(inputFile, targetColumnName, indexColumnName, encoding, sheetName)
        self.topic_param = TopicParams(min, max)
        self.tokenizer_param = TokenizerParams(dockerId=dockerId, dockerSudo=dockerSudo, osType=osType,
                                               pathNeologd=pathNeologdDict, pathUserDict=pathUserDict)
        self.algorithm_param = AlgorithmParams(clusteringModel=model, nSentence=nSentence, nTopWords=nTopWords,
                                                  pathParamConfig=pathParamConfig, pathStopWord=pathStopWord)
        self.lang_params = LangParam(lang=lang)
        self.mail_param = MailParam(mailTo, mailFrom, subject, pathSmtp)
        self.working_param = DirParams(workingDir)


class AlgorithmParams(object):
    def __init__(self, clusteringModel, nSentence, nTopWords, pathParamConfig, pathStopWord):
        self.clusteringModel = clusteringModel
        self.nSentence = nSentence
        self.nTopWords = nTopWords
        self.pathConfig = os.path.abspath(pathParamConfig)
        if os.path.exists(pathStopWord)==False:
            raise IOError("{} does not exist".format(pathStopWord))
        self.pathStopWords = os.path.abspath(pathStopWord)
        self._loadConfigFile()


    def _loadConfigFile(self):
        if os.path.exists(self.pathConfig) == False:
            raise IOError("Config file does not exist. System ends")

        config = ConfigParser.SafeConfigParser()
        config.read(self.pathConfig)

        self.posRemained = config.get('POS', 'pos_remained').decode('utf-8').split(u',')
        self.stopLowLimit = int(config.get('stopWordSetting', 'low_frequency_limit'))
        self.stopHighLimit = float(config.get('stopWordSetting', 'high_ratio_limit'))

        self.nIter = int(config.get('ldaConfig', 'n_iteration'))
        self.randomState = int(config.get('ldaConfig', 'random_state'))



class DirParams(object):
    def __init__(self, workingDir):
        self.workingDir = os.path.abspath(workingDir)
        if os.path.exists(self.workingDir) == False:
            raise IOError("{} does not exist".format(self.workingDir))


class MailParam(object):
    def __init__(self, mailTo, mailFrom, subject, pathSmtp):
        self.mailTo = mailTo
        self.mailFrom = mailFrom
        self.subject = subject
        if self.mailTo == '' and self.mailFrom == '':
            self.is_mail = False
        elif self.mailTo != '' and self.mailFrom == '':
            raise OSError("To send mail both of --mailFrom, --mailTo must be filled")
        elif self.mailTo == '' and self.mailFrom != '':
            raise OSError("To send mail both of --mailFrom, --mailTo must be filled")
        else:
            self.is_mail = True
            if os.path.exists(pathSmtp)==False:
                raise IOError("Smtp config path does not exist in {}".format(pathSmtp))
            self.pathSmtp = os.path.abspath(pathSmtp)


class LangParam(object):
    def __init__(self, lang):
        self.lang = lang


class TokenizerParams(object):

    def __init__(self, dockerId, dockerSudo, osType, pathNeologd, pathUserDict):
        self.dockerId = dockerId
        self.docker_sudo = dockerSudo
        self.osType = osType
        if pathNeologd=='':
            self.pathNeologd = pathNeologd
        else:
            self.pathNeologd = os.path.abspath(pathNeologd)

        if pathUserDict == '':
            self.pathUserDict = ''
        else:
            self.pathUserDict = os.path.abspath(pathUserDict)

        if self.dockerId == '':
            self.mode = 'mecab'
        else:
            self.mode = 'docker'


class FileParams(object):

    def __init__(self, inputFilePath, targetColumnName, indexColumnName, encoding, sheetName):
        if os.path.exists(inputFilePath)==False:
            raise IOError("{} does not exist".format(inputFilePath))

        self.filePath = os.path.abspath(inputFilePath)
        self.targetColumnName = targetColumnName
        self.indexColumnName = indexColumnName
        self.encoding = encoding
        self.sheetName = sheetName
        fileName, fileExtenstion = os.path.splitext(self.filePath)
        if fileExtenstion == '.csv':
            self.mode = 'csv'
        elif fileExtenstion == '.xls' or fileExtenstion == '.xlsx':
            self.mode = 'excel'
        else:
            raise TypeError("input file must be csv or xls or xlsx")


class TopicParams(object):

    def __init__(self, min, max):
        self.min_topic = min
        self.max_topic = max
