#! -*- coding:utf-8 -*-
__author__ = 'kensuke-mi'
import unittest
import sys
import os
import json

import easyTopicClustering.lda_module as lda_wrapper
import easyTopicClustering.rankingInterface as interface
import easyTopicClustering.MorphologySplitter as MorphologySplitter
from easyTopicClustering.models.params import Params
from easyTopicClustering.parser import Parser
from easyTopicClustering.rankingInterface import pre_process
from easyTopicClustering.rankingInterface import main


class TestRankingCodes(unittest.TestCase):

    def test_mecab(self):

        inputFilePath = 'resources/inputSample.csv'
        dockerId = ''
        dockerSudo = False
        pathConfigFile = 'resources/ldaConfig.ini'
        pathStopWords = 'resources/stopWord.csv'

        param_object = Params(projectName='exmaple',
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
                              pathNeologdDict='/usr/local/lib/mecab/dic/mecab-ipadic-neologd/',
                              pathUserDict='',
                              osType='mac',
                              dockerId=dockerId,
                              dockerSudo=dockerSudo,
                              mailTo='',
                              mailFrom='',
                              subject='',
                              workingDir='easyTopicClustering/tmpDir',
                              pathParamConfig=pathConfigFile,
                              pathStopWord=pathStopWords)
        file_parser = Parser(param_object)
        targetSentenceFrame = file_parser.load_data()

        documents, dictionaryObj = pre_process(targetSentenceFrame.targetColumnName.tolist(), param_object)


    def test_docker(self):

        inputFilePath = 'resources/inputSample.csv'
        dockerId = 'aa2685b94082'
        dockerSudo = False
        pathConfigFile = 'resources/ldaConfig.ini'
        pathStopWords = 'resources/stopWord.csv'

        param_object = Params(projectName='exmaple',
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
                              pathNeologdDict='/usr/local/lib/mecab/dic/mecab-ipadic-neologd/',
                              pathUserDict='',
                              osType='mac',
                              dockerId=dockerId,
                              dockerSudo=dockerSudo,
                              mailTo='',
                              mailFrom='',
                              subject='',
                              workingDir='easyTopicClustering/tmpDir',
                              pathParamConfig=pathConfigFile,
                              pathStopWord=pathStopWords)
        file_parser = Parser(param_object)
        targetSentenceFrame = file_parser.load_data()

        documents, dictionaryObj = pre_process(targetSentenceFrame.targetColumnName.tolist(), param_object)

    def test_mecabLda(self):

        inputFilePath = 'resources/inputSample.csv'
        dockerId = ''
        dockerSudo = False
        pathConfigFile = 'resources/ldaConfig.ini'
        pathStopWords = 'resources/stopWord.csv'

        param_object = Params(projectName='exmaple',
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
                              pathNeologdDict='/usr/local/lib/mecab/dic/mecab-ipadic-neologd/',
                              pathUserDict='',
                              osType='mac',
                              dockerId=dockerId,
                              dockerSudo=dockerSudo,
                              mailTo='',
                              mailFrom='',
                              subject='',
                              workingDir='easyTopicClustering/tmpDir',
                              pathParamConfig=pathConfigFile,
                              pathStopWord=pathStopWords)

        main(param_object)



    def test_dockerlda(self):

        min_topics_limit = 3
        max_topics_limit = 5

        dockerId = 'aa2685b94082'
        pathConfigFile = 'resources/ldaConfig.ini'
        configObject = interface.loadConfigFile(pathConfigFile)

        pathStopWords = 'resources/stopWord.csv'
        stopWords = interface.load_csv_data(pathStopWords, 'utf-8')

        targetSentences = [u'エアバスA340 (Airbus A340) は、ヨーロッパの企業連合であるエアバス・インダストリー（後にエアバス）が開発・製造した4発ジェット旅客機である。',
                      u'2008年オーストラリアグランプリは、2008年F1世界選手権第1戦として、2008年3月16日にアルバートパークサーキットで開催された。正式名称は"2008 FORMULA1 ING Australian Grand Prix"',
                      u'A340は長距離路線向けの大型機として開発された。エアバスA300由来の胴体を延長したワイドボディ機で、低翼に配置された主翼下に4発のターボファンエンジンを装備する。',
                      u'米国の航空機メーカーに対抗するため、欧州の航空機メーカーは1970年12月に企業連合「エアバス・インダストリー」を設立した[6]。',
                      u'エアバス内部では、双発機のTA9と4発機のTA11のどちらを先に開発するか議論が重ねられた[16]。'
                      u'インディアン戦争（インディアンせんそう、英: Indian Wars）は、1622年から1890年の間の、アメリカ合衆国における白人入植者（インディアンが呼ぶところのwhite man）によるインディアンの征服戦争の総称。初期のころからインディアンと入植者の小競り合いが続いていたが、移住者の増加とともに列強による植民地戦争とも絡みながら、大規模化していった北米植民地戦争、民族浄化、ジェノサイドである。',
                      u'インディアン戦争は小さな戦争の連続であった。インディアンはそれぞれの歴史を持つ様々な集団であった。戦争の間を通じて、インディアンは「白人」のように一括りで呼べるような単一の民族では無かった。様々なやり方で築かれた社会に住み、地域的なレベルで戦争と和平の決断を下した。ただし、イロコイ連邦や、スー族とシャイアン族、アラパホー族の三部族同盟、またテカムセのような調停者によって実現した一時的な同盟のように、公式の同盟を組んで共闘することが多数見られた。',
                      u'クレイジー・ホースらが参加した、インディアンの連合軍がカスター中佐の第7騎兵隊を撃退全滅させるなどの戦果もあったが、ジェロニモの降伏やウンデット・ニーの虐殺以降、インディアンによる軍事的な反乱はなくなった。',
                      u'2003年、100年近くに及ぶインディアンたちの要求運動によって、「リトルビッグホーンの戦い」の主戦場が「カスター国立記念戦場」から「リトルビッグホーン国立記念戦場」に名称変更された。',
                      u'ニュルンベルクはペグニッツ川の両岸に広がる。ペグニッツ川はこの都市の北東約80kmに湧出し、市内を東西に約14kmにわたって貫いている。',
                      u'ニュルンベルクの土地はコイパー期に形成された柔らかい砂岩からなっている。この町の北側は、一部は海抜600mを超える中低山地のフレンキシェ・シュヴァイツにつながっている。',
                      u'市域は186.38km²である。南部から西部にかけては建物が密集しており、西部は隣のフュルトと、南西はシュタインとほとんど一体化している。',
                      u'旧市街の北の境界はニュルンベルク城が建つ城山であり、市壁の大部分が遺されている。東部からペグニッツ川北岸は公園化されたレーヒェンベルクである。',
                      u'ニュルンベルクの成立は明らかでない。ザクセン、バイエルン、東フランク、ベーメンの境界で、1000年から1400年頃に保護された重要な街道が交わる地点から徐々に成立していったと考えられている。'
                      ]

        dockerInputObj = MorphologySplitter.jsonFormatter(targetSentences)
        temporaryFilePath = MorphologySplitter.saveInTemporaryDir(dockerInputObj, workingDir='easyTopicClustering/tmpDir')
        splittedStrJson = json.loads(MorphologySplitter.DockerCall(temporaryFilePath, container_id=dockerId, have_sudo=False))


        # construct documents
        pos_remained = configObject.get('POS', 'pos_remained').decode('utf-8').split(u',')
        documents = interface.constructDocument(splittedStrJson, pos_remained)
        # stopwordをつくる
        stopWords = set(stopWords)
        pathToSaveDictionary = '../resources/dictionary.dict'

        # 辞書を作る
        low_limit = int(configObject.get('stopWordSetting', 'low_frequency_limit'))
        high_ratio_limit = float(configObject.get('stopWordSetting', 'high_ratio_limit'))
        dictionaryObj = lda_wrapper.createDictionary(documents, stopWords, pathToSaveDictionary,
                                                    low_limit_int=low_limit, high_limit_ratio=high_ratio_limit)
        # corpusを作る
        corpusArray = lda_wrapper.createCorpus(documents, dictionaryObj)
        vocabList = lda_wrapper.createVocaburaryList(dictionaryObj)
        # ldaを実行する

        # check vectorized corpus is correct
        interface._check_doc_term_construction(corpusArray, documents, dictionaryObj)

        #interface.mode_lda(corpusArray, vocabList, min_topics_limit, max_topics_limit, configObject)



def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestRankingCodes))

    return suite