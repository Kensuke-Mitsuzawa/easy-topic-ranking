# what's this?

This is a tiny document clustering project with LDA.

This project works only under python2.7

# Setting up

## Dependency libraries

    pip install -r requirement.txt

## Install

clone this reposiroty into your local and

    python setup.py install

or

    pip install git+https://github.com/Kensuke-Mitsuzawa/easy-topic-ranking

## docker setup

I describe later

    
# Usage

## from python script

1. specify all parameters to be used in script into `easyTopicClustering.models.params.Params`
2. call `easyTopicClustering.rankingInterface.main` argument is just object of Params class
3. (optional) if you want simple summary html, call `easyTopicClustering.send_email.generate_html_report`. This function calls Rscript to generate summary html.

as for example, please see `easyTopicClustering/__main__.py`.

## from command line interface

just call `easyTopicClustering/__main__.py` from command line.