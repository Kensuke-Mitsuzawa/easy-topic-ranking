#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

import unittest
import src.lda_module as lda_wrapper
import lda
import numpy as np

class TestLdaCodes(unittest.TestCase):

    def setUp(self):
        print ''


    def test_lda_lib(self):
        """test lda module works or not

        :return:
        """
        import sys
        import os
        abs_path = os.path.abspath(sys.argv[0])
        abs_path_dir = os.path.dirname(abs_path)
        os.chdir(abs_path_dir)

        X = lda.datasets.load_reuters()
        vocab = lda.datasets.load_reuters_vocab()
        titles = lda.datasets.load_reuters_titles()
        titles_test = titles[:10]

        model = lda.LDA(n_topics=20, n_iter=150, random_state=1)
        model.fit(X)
        topic_word = model.topic_word_

        n_top_words = 8
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
            print u'Topic {}:{}'.format(i, u' '.join(topic_words))

        doc_topic = model.doc_topic_
        for i in range(X.shape[0]):
            print u"top topic: {}".format(doc_topic[i].argmax())


    def test_dictionary(self):
        """test method to construct word to Id dictionary

        :return:
        """
        import sys
        import os
        abs_path = os.path.abspath(sys.argv[0])
        abs_path_dir = os.path.dirname(abs_path)
        os.chdir(abs_path_dir)

        test_documents = ["Human machine interface for lab abc computer applications",
                          "A survey of user opinion of computer system response time",
                          "The EPS user interface management system",
                          "System and human system engineering testing of EPS",
                          "Relation of user perceived response time to error measurement",
                          "The generation of random binary unordered trees",
                          "The intersection graph of paths in trees",
                          "Graph minors IV Widths of trees and well quasi ordering",
                          "Graph minors A survey"]


        test_documents = [
            document.lower().split()
            for document in test_documents
        ]

        setStopwords = set(["for", "a", "of", "the", "and", "to", "in"])

        pathToDictionary = "resources/deerwester.dict"

        dictionaryObject = lda_wrapper.createDictionary(test_documents, setStopwords, pathToDictionary, low_limit_int=2, high_limit_ratio=0.9)
        vectorizedList = lda_wrapper.createCorpus(test_documents, dictionaryObject)

        return vectorizedList, dictionaryObject.token2id


    def test_process(self):
        """test example code to topic clustering

        :return:
        """
        vectorizedList, word2Id = self.test_dictionary()
        vocabList = [
            wordIdTuple[0]
            for wordIdTuple
            in sorted(word2Id.items(), key=lambda x: int(x[1]))
        ]
        distriDatas, topicWordDictionary, DocumentTopicDictionary = lda_wrapper.lda_process(vectorizedList, vocabList, n_topics=5)
        lda_wrapper._plot_topic_word_result(distriDatas['topicDistri'], path_topic_distri='resources/topicWordResult.png')
        lda_wrapper._plot_topic_document_result(distriDatas['docDistri'], path_document_distri_prefix='resources/docWordResult')


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestLdaCodes))

    return suite
