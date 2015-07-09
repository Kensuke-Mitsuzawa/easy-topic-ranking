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
from nLargestDocSummary.parsers.parser import Parser
from nLargestDocSummary.frequency_summarizer import FrequencySummarizer
from nLargestDocSummary.mecab_wrapper.mecab_wrapper import MecabWrapper
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


def format_output(clusteringResults, documents, targetSentenceFrame):
    """

    :param clusteringResults:
    :param documents:
    :param targetSentenceFrame:
    :return:
    """

    items = []
    for topicIdKey in clusteringResults.keys():
        topicRanking = create_topics_ranking(summarise_topics(clusteringResults[topicIdKey]["docs"]))
        for rankingItem in topicRanking:

            # rankingItem is tuple (topicId, [documentIndex])
            # get tokens in document with clustered document index
            tokensInDocOfCluster = [documents[documentIndex] for documentIndex in rankingItem[1]]
            # get sentence of input file with clustered document index
            sentencesOfCluster = [targetSentenceFrame.ix[documentIndex, 'targetColumnName']
                                  for documentIndex in rankingItem[1]]
            items.append(
            {
                "topicParameter": topicIdKey,
                "topicID": rankingItem[0],
                "wordsInTopic": clusteringResults[topicIdKey]["words"][rankingItem[0]].tolist(),
                "docsCluster": len(rankingItem[1]),
                "sentences": sentencesOfCluster,
                "tokenized": tokensInDocOfCluster
            })


    return items


def mode_lda(corpusArray, vocabList, min_topics_limit, max_topics_limit, n_top_words, configObject):

    n_iter = int(configObject.get('ldaConfig', 'n_iteration'))
    random_state = int(configObject.get('ldaConfig', 'random_state'))
    clusteringResults = {}

    for topics in range(min_topics_limit, max_topics_limit+1):
        distriDatas, topicWordDictionary, DocumentTopicDictionary = lda_module.lda_process(corpusArray, vocabList,
                                                                                           n_topics=topics,
                                                                                           n_iter=n_iter,
                                                                                           random_state=random_state,
                                                                                           n_top_words_per_topic=n_top_words)
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


def getBestSentence(clusteredObjects, sentExtractParams):

    newClusteredObjects = []

    pathNeologd = sentExtractParams['pathNeologd']
    osType = sentExtractParams['osType']
    n_sentence = sentExtractParams['n_sentence']

    mecab_wrapper = MecabWrapper(dictType='neologd', osType=osType, pathNeologd=pathNeologd)
    for clusteredObj in clusteredObjects:
        # give clustered document. One cluster = Paragraph
        clustered_documents = u'\n'.join(clusteredObj['sentences'])
        parser_obj = Parser(document=clustered_documents, mecabTokenizer=mecab_wrapper)
        documentObj = parser_obj.make_document()
        fs = FrequencySummarizer(language='ja', documentObj=documentObj)
        summarized = fs.summarize(n=n_sentence)
        clusteredObj['bestSentences'] = summarized
        newClusteredObjects.append(clusteredObj)

    return newClusteredObjects


def main(inputFilePath, inputfileParams, topicParams, sentExtractParams, projectName,
         pathConfigFile, pathStopWords, dockerId, docker_sudo, mode, lang,
         nTopWords, workingDir):
    import codecs

    configObject = loadConfigFile(pathConfigFile)

    targetColumnName = inputfileParams['targetColumnName']
    indexColumnName = inputfileParams['indexColumnName']
    coding = inputfileParams['coding']
    sheet = inputfileParams['sheetName']
    inputFrame = load_data(inputFilePath, coding=coding, sheetName=sheet)
    if targetColumnName not in inputFrame.columns:
        sys.exit('You must select correct clumn name. Now {}'.format(targetColumnName))
    if indexColumnName not in inputFrame.columns:
        sys.exit('You must select correct clumn name. Now {}'.format(indexColumnName))

    targetSentenceFrame = inputFrame.ix[:, [targetColumnName, indexColumnName]]
    targetSentenceFrame.columns = ['targetColumnName', 'indexColumnName']
    targetSentenceFrame.sort(columns='indexColumnName', ascending=True)

    documents, dictionaryObj = pre_process(targetSentenceFrame.targetColumnName.tolist(), configObject, dockerId,
                                           lang, workingDir, pathStopWords, docker_sudo)

    # make corpus
    corpusArray = lda_module.createCorpus(documents, dictionaryObj)
    vocabList = lda_module.createVocaburaryList(dictionaryObj)
    # check vectorized corpus is correct
    _check_doc_term_construction(corpusArray, documents, dictionaryObj)

    min_topics_limit = topicParams['min_topic']
    max_topics_limit = topicParams['max_topic']

    # process main
    if mode == 'lda':
        clusteringResults = mode_lda(corpusArray, vocabList, min_topics_limit, max_topics_limit, nTopWords, configObject)

    # transform into JSON format which has topicParam, topicID, wordsInTopic, sentenceInTopic, tokensInTopic
    clusteredObjects = format_output(clusteringResults, documents, targetSentenceFrame)
    clusteredObjects = getBestSentence(clusteredObjects, sentExtractParams)

    pathOutPutJson = os.path.join(workingDir, '{}.json'.format(projectName))
    with codecs.open(pathOutPutJson, 'w', 'utf-8') as f:
        f.write(json.dumps(obj=clusteredObjects, ensure_ascii=False, indent=4))

    return os.path.abspath(pathOutPutJson)


