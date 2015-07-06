#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

from test_lda_module import TestLdaCodes
from test_ranking_module import TestRankingCodes
import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestLdaCodes))
    suite.addTests(unittest.makeSuite(TestRankingCodes))

    return suite


