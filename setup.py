from setuptools import setup, find_packages
import sys

sys.path.append('./src/')
sys.path.append('./test')


install_requires = ['gensim==0.11.1-1', 'pandas==0.15.2', 'numpy', 'lda']


setup(
    author='Kensuke Mitsuzawa',
    name = 'easyTopicClustering',
    version='0.1',
    test_suite='test_all.suite',
    install_requires = install_requires,
)