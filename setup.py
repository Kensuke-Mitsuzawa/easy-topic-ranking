from setuptools import setup, find_packages
import sys
from easyTopicClustering.rankingInterface import __version__
from easyTopicClustering.rankingInterface import __author__

sys.path.append('./easyTopicClustering/')
sys.path.append('./test')


install_requires = ['gensim==0.11.1-1', 'pandas==0.15.2', 'numpy', 'lda', 'nLargestDocSummary']


setup(
    author=__author__,
    name = 'easyTopicClustering',
    version=__version__,
    test_suite='test_all.suite',
    install_requires = install_requires,
    packages=find_packages(),

)