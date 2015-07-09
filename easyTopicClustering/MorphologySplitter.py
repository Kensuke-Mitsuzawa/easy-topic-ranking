#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

import logging
import subprocess
import sys
import codecs
import json
import os
logging.basicConfig(LEVEL=logging.INFO)


def DockerCall(pathFailedJson, container_id, have_sudo=True):
    if have_sudo==True:
        dockerCallCm = "cat {0} |\
        sudo docker exec -i {1} python2.7 /analysis_code/docker_main.py".format(pathFailedJson, container_id)
    elif have_sudo==False:
        dockerCallCm = "cat {0} |\
        docker exec -i {1} python2.7 /analysis_code/docker_main.py".format(pathFailedJson, container_id)

    logging.debug(msg="called docker with {}".format(dockerCallCm))
    try:
        res = subprocess.check_output( dockerCallCm, shell=True)
    except Exception as e:
        logging.error(e)
        logging.error(e.args)
        logging.error(e.message)
        sys.exit("Failed to call docker container. Check container status.")

    return res


def jsonFormatter(InputList):
    """
    JSON形式に整えられるようにする
    :return:
    """
    return {'inputArray': InputList}


def saveInTemporaryDir(tmpObject, workingDir='tmpDir'):

    temporaryFileObj = os.path.join(workingDir, 'temporary.json')
    fileObj = codecs.open(temporaryFileObj, 'w', 'utf-8')
    fileObj.write(json.dumps(tmpObject, ensure_ascii=False, indent=4))

    return temporaryFileObj


def filterTokens(processedObjects):
    # remove tokens except Nouns
    filter = lambda x: True if u'名詞' in x[1] else False
    filteredObjects = {}

    for processedObj in processedObjects:
        originalName = processedObj['original']
        # takes only nouns whose pos is '名詞'
        Nouns = [noun[0] for noun in processedObj['analyzed'] if filter(noun) == True]

        filteredObjects[originalName] = Nouns

    return filteredObjects


def __PostProcessDocker(failedJson, processedRes):
    filteredObjects = filterTokens(processedRes)
    # merge 2 dict objects. key is originalName
    mergedFailedObjects = []
    for originalObject in failedJson:
        originalObject.update({'nouns': filteredObjects[originalObject['originalName']]})
        mergedFailedObjects.append(originalObject)

    return mergedFailedObjects


def morphogicalSplitMain(pathFailedJson, failedJsonObjects, container_id):
    processedRes = DockerCall(pathFailedJson, container_id=container_id)
    processedObjects = json.loads(processedRes)
    mergedObjects = __PostProcessDocker(failedJsonObjects, processedObjects)

    return mergedObjects


def __test():
    # test docker container ID aa2685b94082
    import sys
    import os
    abs_path = os.path.abspath(sys.argv[0])
    abs_path_dir = os.path.dirname(abs_path)
    os.chdir(abs_path_dir)

    pathFailedJson = '../resources/fullTextSearchFailedJson.json'
    with codecs.open(pathFailedJson, 'r', 'utf-8') as f:
        failedJson = json.load(f)
    formattedInput = jsonFormatter(failedJson)

    processedRes = DockerCall(json.dumps(formattedInput, ensure_ascii=True), container_id="aa2685b94082")
    processedObjects = json.loads(processedRes)
    mergedObjects = __PostProcessDocker(failedJson, processedObjects)


if __name__ == '__main__':
    __test()