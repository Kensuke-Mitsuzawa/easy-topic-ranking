#! -*- coding: utf-8 -*-
import lda_module
import MorphologySplitter
import pandas as pd
import os
import sys
import logging
import json
import ConfigParser
from parser import Parser as FileParser
from easyTopicClustering.models.params import Params
from nLargestDocSummary.parsers.parser import Parser
from nLargestDocSummary.frequency_summarizer import FrequencySummarizer
from nLargestDocSummary.mecab_wrapper.mecab_wrapper import MecabWrapper

__author__ = 'kensuke-mi'
__version__ = 0.2


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


def load_csv_data(pathStopWords, coding):
    stopFrame = pd.read_csv(pathStopWords, encoding=coding,header=0)
    stopWordsList = [unicode(item)
                     for item in stopFrame.ix[:, "stopwrods"].tolist()]

    return stopWordsList


def pre_process(targetSentences, param_object):

    # construct documents
    pos_remained = param_object.algorithm_param.posRemained

    if param_object.lang_params.lang == 'ja':
        if param_object.tokenizer_param.mode=='docker':
            dockerInputObj = MorphologySplitter.jsonFormatter(targetSentences)
            temporaryFilePath = MorphologySplitter.saveInTemporaryDir(dockerInputObj,
                                                                      workingDir=param_object.working_param.workingDir)
            splittedStrJson = json.loads(MorphologySplitter.DockerCall(temporaryFilePath,
                                                                       container_id=param_object.tokenizer_param.dockerId,
                                                                       have_sudo=param_object.tokenizer_param.docker_sudo))
            documents = constructDocument(splittedStrJson, pos_remained)

        elif param_object.tokenizer_param.mode=='mecab':
            from nLargestDocSummary.mecab_wrapper.mecab_wrapper import MecabWrapper
            pathNeologd = param_object.tokenizer_param.pathNeologd
            osType = param_object.tokenizer_param.osType

            mecab_wrapper = MecabWrapper(dictType='neologd', osType=osType, pathNeologd=pathNeologd)
            documentsList = [mecab_wrapper.tokenize(sentence=s, is_feature=True) for s in targetSentences]
            documents = [
                [t[0]
                    for t in s
                    if t[1][0] in pos_remained
                ]
                for s in documentsList]

    elif param_object.lang_params.lang == 'en':
        documents = [
            [word.lower() for word in sentence.split(u' ')]
            for sentence in targetSentences]

    # stopwordをつくる
    stopWords = load_csv_data(param_object.algorithm_param.pathStopWords, 'utf-8')
    stopWords = set(stopWords)
    pathToSaveDictionary = '../resources/dictionary.dict'

    # 辞書を作る
    low_limit = param_object.algorithm_param.stopLowLimit
    high_ratio_limit = param_object.algorithm_param.stopHighLimit
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
            # get sentence of input file with clustered document index
            sentencesOfCluster = [targetSentenceFrame.ix[documentIndex, 'targetColumnName']
                                  for documentIndex in rankingItem[1]]
            items.append(
            {
                "topicParameter": topicIdKey,
                "topicID": rankingItem[0],
                "wordsInTopic": clusteringResults[topicIdKey]["words"][rankingItem[0]].tolist(),
                "docsCluster": len(rankingItem[1]),
                "sentences": sentencesOfCluster
            })


    return items


def format_table(clusteringResults, documents, targetSentenceFrame):
    assert isinstance(clusteringResults, dict)
    assert isinstance(documents, list)
    assert isinstance(targetSentenceFrame, pd.DataFrame)

    row_stack = []
    for topicIdKey in clusteringResults.keys():
        topicRanking = create_topics_ranking(summarise_topics(clusteringResults[topicIdKey]["docs"]))
        assert isinstance(topicRanking, list)
        for rankingItem in topicRanking:
            # get sentence of input file with clustered document index
            sentencesOfCluster = [
                {
                    'topic_parameter': topicIdKey,
                    'topic_id': rankingItem[0],
                    'document_index': documentIndex,
                    'sentence': targetSentenceFrame.ix[documentIndex, 'targetColumnName']
                }
                for documentIndex in rankingItem[1]
                ]
            row_stack += sentencesOfCluster
    table = pd.DataFrame(row_stack)
    return table.reindex_axis(['topic_parameter', 'topic_id', 'document_index', 'sentence'], axis=1)


def mode_lda(corpusArray, vocabList, param_object):

    min_topics_limit = param_object.topic_param.min_topic
    max_topics_limit = param_object.topic_param.max_topic

    n_iter = param_object.algorithm_param.nIter
    random_state = param_object.algorithm_param.randomState
    clusteringResults = {}

    for topics in range(min_topics_limit, max_topics_limit+1):
        distriDatas, topicWordDictionary, DocumentTopicDictionary = lda_module.lda_process(corpusArray, vocabList,
                                                                                           n_topics=topics,
                                                                                           n_iter=n_iter,
                                                                                           random_state=random_state,
                                                                                           n_top_words_per_topic=param_object.algorithm_param.nTopWords)
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


def getBestSentence(clusteredObjects, n_sentence, tokenizer_param):

    newClusteredObjects = []

    pathNeologd = tokenizer_param.pathNeologd
    osType = tokenizer_param.osType

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


def main(param_object):
    assert isinstance(param_object, Params)
    import codecs

    file_parser = FileParser(param_object)
    targetSentenceFrame = file_parser.load_data()

    documents, dictionaryObj = pre_process(targetSentenceFrame.targetColumnName.tolist(), param_object)

    # make corpus
    corpusArray = lda_module.createCorpus(documents, dictionaryObj)
    vocabList = lda_module.createVocaburaryList(dictionaryObj)
    # check vectorized corpus is correct
    _check_doc_term_construction(corpusArray, documents, dictionaryObj)

    # process main
    if param_object.algorithm_param.clusteringModel == 'lda':
        clusteringResults = mode_lda(corpusArray, vocabList, param_object)

    # transform into JSON format which has topicParam, topicID, wordsInTopic, sentenceInTopic, tokensInTopic
    clusteredObjects = format_output(clusteringResults, documents, targetSentenceFrame)
    clusteredObjects = getBestSentence(clusteredObjects, param_object.algorithm_param.nSentence, param_object.tokenizer_param)

    id_sentence_table = format_table(clusteringResults, documents, targetSentenceFrame)
    assert isinstance(id_sentence_table, pd.DataFrame)

    pathOutPutJson = os.path.join(param_object.working_param.workingDir, '{}.json'.format(param_object.projectName))
    with codecs.open(pathOutPutJson, 'w', 'utf-8') as f:
        f.write(json.dumps(obj=clusteredObjects, ensure_ascii=False, indent=4))

    pathOutPutTSV = os.path.join(param_object.working_param.workingDir, '{}.tsv'.format(param_object.projectName))
    id_sentence_table.to_csv(pathOutPutTSV, sep='\t', index=False, index_label=False, encoding='utf-8', quoting=2)

    return os.path.abspath(pathOutPutJson)