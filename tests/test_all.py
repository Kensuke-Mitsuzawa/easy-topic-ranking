#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

from tests.test_lda_module import TestLdaCodes
from tests.test_ranking_module import TestRankingCodes
from tests.test_interface import TestCommandLineInterface
from tests.test_parser import TestParser
import unittest


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCommandLineInterface))
    suite.addTests(unittest.makeSuite(TestLdaCodes))
    suite.addTests(unittest.makeSuite(TestRankingCodes))
    suite.addTests(unittest.makeSuite(TestParser))

    return suite


