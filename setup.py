from setuptools import setup, find_packages
import sys

sys.path.append('./src/')
sys.path.append('./test')


extras_require = {}

install_requires = ['gensim==0.11.1-1', 'lda==1.0.2', 'pandas==0.15.2', 'numpy']


setup(
    author='Kensuke Mitsuzawa',
    name = 'easyTopicClustering',
    version='0.1',
    package=find_packages(),
    test_suite='test_all.suite',
    install_requires = install_requires,
    extras_require=extras_require,
    package_dir={'': 'src'},
)