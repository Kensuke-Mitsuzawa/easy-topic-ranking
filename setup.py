from setuptools import setup, find_packages
import sys
__author__ = 'kensuke-mi'
__version__ = 0.22

#sys.path.append('./easyTopicClustering/')
#sys.path.append('./tests')


install_requires = ['typing', 'gensim==0.11.1-1', 'pandas', 'numpy', 'lda', 'nLargestDocSummary', 'xlwt', 'xlrd', 'JapaneseTokenizer']
dependency_links=['git+ssh://git@github.com/Kensuke-Mitsuzawa/ja-sentence-search-Nlargest.git#egg=nLargestDocSummary']


setup(
    author=__author__,
    name = 'easyTopicClustering',
    version=__version__,
    test_suite='test_all.suite',
    install_requires = install_requires,
    packages=find_packages(),
    dependency_links=dependency_links,
    include_package_data=True,
    zip_safe=False
)