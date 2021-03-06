#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

import sys
import os
import argparse
import logging
from easyTopicClustering.rankingInterface import main
from easyTopicClustering.send_email import generate_html_report
from easyTopicClustering.models.params import Params
logging.basicConfig(level=logging.INFO)


def __exmaple_usage():
    inputFilePath = '../resources/inputSample.csv'
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
                          sheetName='',
                          min=2,
                          max=5,
                          model='lda',
                          nTopWords=15,
                          pathUserDict='',
                          nSentence=2,
                          pathParamConfig=pathConfigFile,
                          pathStopWord=pathStopWords,
                          pathNeologdDict='/usr/local/lib/mecab/dic/mecab-ipadic-neologd/',
                          osType='mac', dockerId='', dockerSudo=False,
                          mailTo='', mailFrom='', subject='', pathSmtp='', workingDir=working_dir)


    pathOutPutJson = main(param_object)
    pathResource = os.path.abspath('../resources')

    abs_path_script = __file__
    abs_path_dir = abs_path_script.replace('tests/test_interface.py', '').replace('/c', '')

    generate_html_report(pathScriptDir=abs_path_dir, pathToJson=pathOutPutJson, projetcName=projectName,
                         resourceDir=pathResource, mailFrom='', mailTo='', pathSmtp='', sendMail=False)


    return pathOutPutJson



if __name__ == '__main__':
    abs_path = os.path.abspath(sys.argv[0])
    abs_path_dir = os.path.dirname(abs_path)
    os.chdir(abs_path_dir)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--lang', default='ja', required=False, help='language selection ja/en. Default is ja')
    parser.add_argument('--dockerId', required=False, default='', help='dockerId to preprocess Japanese input')
    parser.add_argument('--dockerSudo', required=False, default=False, action='store_true', help='if added, call docker with sudo')
    parser.add_argument('--mode', required=False, default='lda', help='method to make cluster. Default is lda')
    parser.add_argument('--encoding', required=False, default='utf-8', help='character encode of input file. Default is utf-8')
    parser.add_argument('--targetColumnName', required=False, default='contents', help='column name of data in file.')
    parser.add_argument('--indexColumnName', required=False, default='docIndex', help='index of documents')
    parser.add_argument('--sheetName', required=False, default='Sheet1', help='sheetName in which data is.')

    # mail setting
    parser.add_argument('--subject', required=False, default=str, help='subject')
    parser.add_argument('--mailFrom', required=False, default='', help='mail address from')
    parser.add_argument('--mailTo', required=False, default='', help='mail address to')
    parser.add_argument('--pathSmtpConf', required=False, default='', help='path to smtp setting file csv')

    # config file option
    parser.add_argument('--pathConfigFile', required=True, help='path to config file. Please specify correct config file for method')
    parser.add_argument('--pathStopWords', required=True, help='')
    # input file option
    parser.add_argument('--inputFilePath', required=True, help='input file. csv or xlsx or xls file is plausible.')

    parser.add_argument('--projectName', required=True, help='project name of this cluster analysis. This name is used file prefix.')
    parser.add_argument('--min_topics', required=True, type=int, help='minimum number of topics')
    parser.add_argument('--max_topics', required=True, type=int, help='maximum number of topics')
    parser.add_argument('--n_top_words', required=True, type=int, help='N of top words for each cluster')

    # sentence extractor params
    parser.add_argument('--n_extract_sent', required=False, default=2, type=int, help='N of representative sentences in cluster')
    parser.add_argument('--pathNeologd', required=False, default='/usr/local/lib/mecab/dic/mecab-ipadic-neologd/',
                        type=str, help='path to mecab neologd dictionary')
    parser.add_argument('--pathUserDict', required=False, default='',
                        type=str, help='path to mecab userdict dictionary')
    parser.add_argument('--osType', required=False, default='mac', type=str, help='os type. mac or centOs')


    parser.add_argument('--workingDir', required=True, help='tmporary working Dir')
    args = parser.parse_args()


    param_object = Params(projectName=args.projectName, lang=args.lang, inputFile=args.inputFilePath,
                          targetColumnName=args.targetColumnName, indexColumnName=args.indexColumnName,
                          encoding=args.encoding, sheetName=args.sheetName, min=args.min_topics, max=args.max_topics,
                          model=args.mode, nSentence=args.n_extract_sent, nTopWords=args.n_top_words,
                          pathUserDict=args.pathUserDict, pathNeologdDict=args.pathNeologd,
                          pathParamConfig=args.pathConfigFile, pathStopWord=args.pathStopWords,
                          osType=args.osType, dockerId=args.dockerId, dockerSudo=args.dockerSudo,
                          mailTo=args.mailTo, mailFrom=args.mailFrom, subject=args.subject, pathSmtp=args.pathSmtpConf, 
                          workingDir=args.workingDir)
    pathOutPutJson = main(param_object)

    pathResource = os.path.abspath(os.path.join(args.workingDir, param_object.projectName))
    generate_html_report(pathScriptDir=abs_path_dir, pathToJson=pathOutPutJson,
                         projetcName=param_object.projectName, resourceDir=pathResource,
                         mailFrom=param_object.mail_param.mailFrom,
                         mailTo=param_object.mail_param.mailTo, sendMail=param_object.mail_param.is_mail,
                         pathSmtp='')
                         #pathSmtp=param_object.mail_param.pathSmtp)
