#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

import lda_module
import MorphologySplitter
import pandas as pd
import os
import sys
import logging
import json
import ConfigParser
import argparse
logging.basicConfig(level=logging.INFO)


def _check_doc_term_construction(corpusArray, targetSentences, dictionaryObj):
    # check constructed doc-term is correct
    id_word_dictionary = {
        v:k for k, v in dictionaryObj.token2id.items()
    }
    for documenIndex, vectorizedSentence in enumerate(corpusArray):
        for wordIndex, wordFreq in enumerate(vectorizedSentence):
            word = id_word_dictionary[wordIndex]
            countedWordFreq = targetSentences[documenIndex].count(word)

            logging.debug(u'wordId:{} wordId Frequency:{} realWord:{} word Frequency:{}'.format(wordIndex, wordFreq, word, countedWordFreq))
            if wordFreq != 0: assert word in targetSentences[documenIndex]
            assert countedWordFreq == wordFreq


def create_topics_ranking(topic_document_dictionary):
    # 集計結果からランキングを作成する
    sortedResult = sorted(topic_document_dictionary.items(), key=lambda x: len(x[1]), reverse=True)

    return sortedResult


def summarise_topics(DocumentTopicDictionary):
    # トピックごとに文書数を集計する
    topic_document_dictionary = {}
    for documentId, topic in DocumentTopicDictionary.items():
        if topic not in topic_document_dictionary:
            topic_document_dictionary[topic] = [documentId]
        else:
            topic_document_dictionary[topic].append(documentId)

    return topic_document_dictionary


def generate_html_report(pathScriptDir, pathToJson, projetcName, resourceDir, mailFrom, mailTo, sendMail=False):
    import subprocess
    projectRootDir = pathScriptDir.split('src')[0]
    #os.chdir(pathScriptDir)

    path_to_R_dir = os.path.join(projectRootDir, 'Rscripts')
    pathToRscript = os.path.join(projectRootDir, 'Rscripts/sendHtmlMail.R')

    if sendMail == True:
        generate_html_Rcommand = '{scirptPath} --script_dir {dirPath} --input_json {jsonPath}\
         --save_dir {savePath} --project_name {project} --mail_send --email_address_from {mailFrom}\
          --email_address {mailTo} '.format(**{'scirptPath': pathToRscript,
                                               'dirPath': path_to_R_dir,
                                               'jsonPath': pathToJson,
                                               'savePath': resourceDir,
                                               'project': projetcName,
                                               'mailFrom': mailFrom, 'mailTo': mailTo})
    else:
        generate_html_Rcommand = '{scirptPath} --script_dir {dirPath} --input_json {jsonPath}\
         --save_dir {savePath} --project_name {project}'.format(**{'scirptPath': pathToRscript,
                                                                 'dirPath': path_to_R_dir,
                                                                 'jsonPath': pathToJson,
                                                                 'savePath': resourceDir,
                                                                 'project': projetcName})

    logging.info(generate_html_Rcommand)
    try:
        subprocess.check_output(generate_html_Rcommand, shell=True)
    except Exception as e:
        logging.error(e)
        logging.error(e.args)
        logging.error(e.message)
        sys.exit("Failed to call Rscript. Check Command to call Rscript")

    path_to_html = '{}/{}-report.html'.format(resourceDir, projetcName)

    return path_to_html


def loadConfigFile(pathToConfigFile):
    if os.path.exists(pathToConfigFile) == False:
        sys.exit("Config file does not exist. System ends")

    config = ConfigParser.SafeConfigParser()
    config.read(pathToConfigFile)

    return config


def constructDocument(splittedStrJson, posRemained):

    documents = [
        [token[0]
        for token in analyzedObj['analyzed']
        if token[1][0] in posRemained
        ]
        for analyzedObj in splittedStrJson
        ]
    return documents


def load_data(filePath, coding='utf-8', sheetName='Sheet1'):

    if os.path.exists(filePath) == False:
        sys.exit('{} does not exist. System Exists'.format(filePath))

    # 入力はcsvかxlsxの形式
    fileName, fileExtenstion = os.path.splitext(filePath)

    if fileExtenstion == '.csv':
        inputFrame = pd.read_csv(filePath, encoding=coding, header=0)
    elif fileExtenstion == '.xlsx' or fileExtenstion == '.xls':
        ExcelObject = pd.ExcelFile(filePath)
        inputFrame = ExcelObject.parse(sheetName)
    else:
        sys.exit('Invalid fileExtenstion {}'.format(fileExtenstion))

    return inputFrame


def load_csv_data(pathStopWords, coding):
    stopFrame = pd.read_csv(pathStopWords, encoding=coding,header=0)
    stopWordsList = [unicode(item)
                     for item in stopFrame.ix[:, "stopwrods"].tolist()]

    return stopWordsList


def pre_process(targetSentences, configObject, dockerId, lang='ja', workingDir='./tmpDir',
                pathStopWords='../resources/stopWord.csv', docker_sudo=True):

    if lang=='ja':
        dockerInputObj = MorphologySplitter.jsonFormatter(targetSentences)
        temporaryFilePath = MorphologySplitter.saveInTemporaryDir(dockerInputObj, workingDir=workingDir)
        splittedStrJson = json.loads(MorphologySplitter.DockerCall(temporaryFilePath, container_id=dockerId, have_sudo=docker_sudo))
        # construct documents
        pos_remained = configObject.get('POS', 'pos_remained').decode('utf-8').split(u',')
        documents = constructDocument(splittedStrJson, pos_remained)
    elif lang=='en':
        documents = [
            [word.lower() for word in sentence.split(u' ')]
            for sentence in targetSentences]

    # stopwordをつくる
    stopWords = load_csv_data(pathStopWords, 'utf-8')
    stopWords = set(stopWords)
    pathToSaveDictionary = '../resources/dictionary.dict'

    # 辞書を作る
    low_limit = int(configObject.get('stopWordSetting', 'low_frequency_limit'))
    high_ratio_limit = float(configObject.get('stopWordSetting', 'high_ratio_limit'))
    dictionaryObj = lda_module.createDictionary(documents, stopWords, pathToSaveDictionary,
                                                low_limit_int=low_limit, high_limit_ratio=high_ratio_limit)

    return documents, dictionaryObj


def format_output(clusteringResults):
    items = []
    for topicIdKey in clusteringResults.keys():
        topicRanking = create_topics_ranking(summarise_topics(clusteringResults[topicIdKey]["docs"]))
        for rankingItem in topicRanking:
            items.append(
            {
                "topicParameter": topicIdKey,
                "topicID": rankingItem[0],
                "wordsInTopic": clusteringResults[topicIdKey]["words"][rankingItem[0]].tolist(),
                "docsCluster": len(rankingItem[1])
            })


    return items


def mode_lda(corpusArray, vocabList, min_topics_limit, max_topics_limit, configObject):

    n_iter = int(configObject.get('ldaConfig', 'n_iteration'))
    random_state = int(configObject.get('ldaConfig', 'random_state'))
    clusteringResults = {}

    for topics in range(min_topics_limit, max_topics_limit+1):
        distriDatas, topicWordDictionary, DocumentTopicDictionary = lda_module.lda_process(corpusArray, vocabList,
                                                                                           n_topics=topics,
                                                                                           n_iter=n_iter,
                                                                                           random_state=random_state)
        topic_document_dictionary = summarise_topics(DocumentTopicDictionary)
        sortedResult = create_topics_ranking(topic_document_dictionary)

        logging.info(u'document clustering with {} topics'.format(topics))
        for topicId_value_tuple in sortedResult:
            topicId = topicId_value_tuple[0]
            n_document = len(topicId_value_tuple[1])
            logging.info(u'TopicId {} has {} documents'.format(topicId, n_document))
            logging.info(u'TopicId {} has words {}'.format(topicId, u' '.join(topicWordDictionary[topicId].tolist())))
        logging.info(u'-'*30)
        clusteringResults[topics] = {"words": topicWordDictionary, "docs": DocumentTopicDictionary}

    return clusteringResults


def main(inputFilePath, inputfileParams, topicParams, projectName,
         pathConfigFile, pathStopWords, dockerId, docker_sudo, mode, lang, workingDir):
    import codecs

    configObject = loadConfigFile(pathConfigFile)

    targetColumnName = inputfileParams['targetColumnName']
    coding = inputfileParams['coding']
    sheet = inputfileParams['sheetName']
    inputFrame = load_data(inputFilePath, coding=coding, sheetName=sheet)
    targetSentences = inputFrame.ix[:, targetColumnName].tolist()


    documents, dictionaryObj = pre_process(targetSentences, configObject, dockerId, lang,
                                           workingDir, pathStopWords, docker_sudo)

    # corpusを作る
    corpusArray = lda_module.createCorpus(documents, dictionaryObj)
    vocabList = lda_module.createVocaburaryList(dictionaryObj)
    # check vectorized corpus is correct
    _check_doc_term_construction(corpusArray, documents, dictionaryObj)

    min_topics_limit = topicParams['min_topic']
    max_topics_limit = topicParams['max_topic']
    if mode == 'lda':
        clusteringResults = mode_lda(corpusArray, vocabList, min_topics_limit, max_topics_limit, configObject)

    outputJson = format_output(clusteringResults)
    pathOutPutJson = os.path.join(workingDir, '{}.json'.format(projectName))
    with codecs.open(pathOutPutJson, 'w', 'utf-8') as f:
        f.write(json.dumps(obj=outputJson, ensure_ascii=False, indent=4))

    return os.path.abspath(pathOutPutJson)


def __exmaple_usage():
    abs_path = os.path.abspath(sys.argv[0])
    abs_path_dir = os.path.dirname(abs_path)
    os.chdir(abs_path_dir)

    inputFilePath = '../resources/inputSample.csv'
    inputfileParams = {'targetColumnName': 'contents', 'coding': 'utf-8', 'sheetName': ''}
    projectName = 'example'

    pathConfigFile = '../resources/ldaConfig.ini'
    pathStopWords = '../resources/stopWord.csv'

    docker_sudo = False
    dockerID = 'aa2685b94082'

    topicParams = {'min_topic': 3, 'max_topic': 5}
    mode = 'lda'

    outputJson = main(inputFilePath, inputfileParams=inputfileParams, topicParams=topicParams, pathConfigFile=pathConfigFile,
         pathStopWords=pathStopWords, dockerId=dockerID, docker_sudo=docker_sudo, mode=mode, workingDir='tmpDir')

    import codecs
    pathOutPutJson = os.path.abspath('../resources/{}.json'.format(projectName))
    with codecs.open(pathOutPutJson, 'w', 'utf-8') as f:
        f.write(json.dumps(obj=outputJson, ensure_ascii=False, indent=4))

    pathResource = os.path.abspath('../resources')
    generate_html_report(pathScriptDir=abs_path_dir, pathToJson=pathOutPutJson, projetcName=projectName,
                         resourceDir=pathResource, mailFrom='', mailTo='', sendMail=False)

    return outputJson



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
    parser.add_argument('--sheetName', required=False, default='', help='sheetName in which data is.')

    # mail setting
    parser.add_argument('--sendMail', required=False, default=False, action='store_true', help='if added, send email.')
    parser.add_argument('--mailFrom', required=False, default='', help='mail address from')
    parser.add_argument('--mailTo', required=False, default='', help='mail address to')

    # config file option
    parser.add_argument('--pathConfigFile', required=True, help='path to config file. Please specify correct config file for method')
    parser.add_argument('--pathStopWords', required=True, help='')
    # input file option
    parser.add_argument('--inputFilePath', required=True, help='input file. csv or xlsx or xls file is plausible.')

    parser.add_argument('--projectName', required=True, help='project name of this cluster analysis. This name is used file prefix.')
    parser.add_argument('--min_topics', required=True, type=int, help='minimum number of topics')
    parser.add_argument('--max_topics', required=True, type=int, help='maximum number of topics')

    parser.add_argument('--workingDir', required=True, help='tmporary working Dir')
    args = parser.parse_args()

    fileParams = {'targetColumnName': args.targetColumnName, 'coding': args.encoding, 'sheetName': args.sheetName}
    topicParams = {'min_topic': args.min_topics, 'max_topic': args.max_topics}

    if args.lang=='ja' and args.dockerId=='':
        sys.exit('You must specify dockerId if lang is ja. System Ends')

    pathOutPutJson = main(inputFilePath=args.inputFilePath, inputfileParams=fileParams, topicParams=topicParams,
         projectName=args.projectName, pathConfigFile=args.pathConfigFile,
         pathStopWords=args.pathStopWords, dockerId=args.dockerId, docker_sudo=args.dockerSudo,
         mode=args.mode, lang=args.lang, workingDir=args.workingDir)

    pathResource = os.path.abspath('../resources')
    generate_html_report(pathScriptDir=abs_path_dir, pathToJson=pathOutPutJson, projetcName=args.projectName,
                         resourceDir=pathResource, mailFrom=args.mailFrom, mailTo=args.mailTo, sendMail=args.sendMail)