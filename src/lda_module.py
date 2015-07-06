#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

from gensim import corpora
import numpy as np
import lda
import lda.datasets
import logging
logging.basicConfig(level=logging.INFO)


def __removeStopWords(documents, stopWords):
    """

    :param documents 2 dimension list:
    :param stopWords set object:
    :return:
    """
    texts = [
        [word for word in document if word not in stopWords]
        for document in documents]

    return texts


def __filterOutLowFreqWords(dictionary, low_limit_int_param, high_limit_ratio_param):
    """

    :param dictionary:
    :param low_limit_int_param:
    :param high_limit_ratio_param:
    :return:
    """

    if low_limit_int_param == 0 and high_limit_ratio_param > 0:
        dictionary.filter_extremes(no_above=high_limit_ratio_param)
    elif low_limit_int_param != 0 and high_limit_ratio_param == 0:
        dictionary.filter_extremes(no_below=low_limit_int_param)
    elif low_limit_int_param == 0 and high_limit_ratio_param == 0:
        return dictionary
    else:
        dictionary.filter_extremes(no_below=low_limit_int_param, no_above=high_limit_ratio_param)

    return dictionary


def createVocaburaryList(dictionaryObj):
    vocabList = [
        wordIdTuple[0]
        for wordIdTuple
        in sorted(dictionaryObj.token2id.items(), key=lambda x: int(x[1]))
    ]

    return vocabList


def createDictionary(documents, setStopwords, pathToDictionary, low_limit_int, high_limit_ratio):
    """

    :param documents 2 dimension list:
    :param setStopwords:
    :param pathToDictionary:
    :return:
    """

    texts = __removeStopWords(documents, setStopwords)

    dictionary = corpora.Dictionary(texts)
    # 最低出現回数(TF)と最高出現率を指定してfiltering
    dictionary = __filterOutLowFreqWords(dictionary, low_limit_int_param=low_limit_int, high_limit_ratio_param=high_limit_ratio)
    dictionary.save(pathToDictionary)

    return dictionary


def createCorpus(documents, dictionaryObject):

    # construct list constructed with (document, wordFrequency)
    # each element is frequency of word in a document
    initializedCorpus = [
        [
            0 for col in range(len(dictionaryObject.token2id.keys()))
        ]
        for row in range(len(documents))
    ]

    for documentsIndex, document in enumerate(documents):
        for word in document:
            if word in dictionaryObject.token2id.keys():
                wordId = dictionaryObject.token2id[word]
                wordFrequency = document.count(word)
                initializedCorpus[documentsIndex][wordId] = wordFrequency

    corpus_numpy = np.array(initializedCorpus)

    return corpus_numpy


def lda_process(documentNumpyArray, vocabList, n_topics, n_iter=150, random_state=1, n_top_words_per_topic=8):
    """

    :param documentNumpyArray:
    :param vocabList:
    :param n_topics:
    :param n_iter:
    :param random_state:
    :param n_top_words_per_topic:
    :return:
    """

    model = lda.LDA(n_topics=n_topics, n_iter=n_iter, random_state=random_state)
    model.fit(documentNumpyArray)
    topic_word = model.topic_word_

    topicWordDictionary = {}
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(vocabList)[np.argsort(topic_dist)][:-(n_top_words_per_topic+1):-1]
        logging.info(u'Topic {}:{}'.format(i, u' '.join(topic_words)))
        topicWordDictionary[i] = topic_words

    DocumentTopicDictionary = {}
    doc_topic = model.doc_topic_
    for i in range(documentNumpyArray.shape[0]):
        logging.info(u"document id: {} top topic: {}".format(i, doc_topic[i].argmax()))
        DocumentTopicDictionary[i] = doc_topic[i].argmax()


    return {'topicDistri': topic_word, 'docDistri': doc_topic}, topicWordDictionary, DocumentTopicDictionary


def _plot_topic_word_result(topic_word, path_topic_distri="topicWordResult.png"):

    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('Agg')
    plt.style.use('ggplot')

    n_topics = topic_word.shape[0]
    n_words = topic_word.shape[1]
    f, ax= plt.subplots(n_topics, 1, figsize=(8, 6), sharex=True)
    for i in range(0, n_topics):
        ax[i].stem(topic_word[i, :], linefmt='b-', markerfmt='bo', basefmt='w-')
        ax[i].set_xlim(0, n_words)
        ax[i].set_ylim(0, 0.9)
        ax[i].set_ylabel("Prob")
        ax[i].set_title("topic {}".format(i))

    ax[4].set_xlabel("word")
    plt.tight_layout()
    plt.savefig( path_topic_distri )



def _plot_topic_document_result(doc_topic, path_document_distri_prefix='docWordResult'):
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('Agg')
    plt.style.use('ggplot')
    plt.figure()

    n_limit_per_one_graph = 5
    n_docs = doc_topic.shape[0]
    n_topics = doc_topic.shape[1]
    # initialize graph plot
    f, ax = plt.subplots(n_limit_per_one_graph, 1, figsize=(8, 6), sharex=True)
    graph_row_index = 0

    for i in range(0, n_docs - 1):
        ax[graph_row_index].stem(doc_topic[i, :], linefmt='r-', markerfmt='ro', basefmt='w-')
        ax[graph_row_index].set_xlim(-1, n_topics)
        ax[graph_row_index].set_ylim(0, 1)
        ax[graph_row_index].set_ylabel("Prob")
        ax[graph_row_index].set_title("Document {}".format(i))
        graph_row_index += 1

        if i % (n_limit_per_one_graph -1) == 0 and i != 0:
            plt.tight_layout()
            plt.savefig( '{}_{}.png'.format(path_document_distri_prefix, i) )
            plt.figure()
            # reset graph plot
            f, ax = plt.subplots(n_limit_per_one_graph, 1, figsize=(8, 6), sharex=True)
            graph_row_index = 0

    # write out plot at last
    plt.tight_layout()
    plt.savefig( '{}_{}.png'.format(path_document_distri_prefix, i) )




if __name__ == '__main__':
    print ''

