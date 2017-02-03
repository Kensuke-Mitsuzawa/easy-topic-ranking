#! -*- coding: utf-8 -*-
__author__ = 'kensuke-mi'

import os
import sys
from easyTopicClustering import logger_unit
logger = logger_unit.logger

def generate_html_report(pathScriptDir, pathToJson, projetcName, resourceDir, mailFrom, mailTo, pathSmtp, sendMail=False):
    import subprocess
    projectRootDir = pathScriptDir.split('easyTopicClustering')[0]

    path_to_R_dir = os.path.join(projectRootDir, 'Rscripts')
    pathToRscript = os.path.join(projectRootDir, 'Rscripts/sendHtmlMail.R')

    if sendMail == True:
        generate_html_Rcommand = '{scirptPath} --script_dir {dirPath} --input_json {jsonPath}\
         --save_dir {savePath} --project_name {project} --mail_send --email_address_from {mailFrom}\
          --email_address {mailTo} --path_smtp_conf {pathSmtp}'.format(**{'scirptPath': pathToRscript,
                                               'dirPath': path_to_R_dir,
                                               'jsonPath': pathToJson,
                                               'savePath': resourceDir,
                                               'project': projetcName,
                                               'mailFrom': mailFrom, 'mailTo': mailTo,
                                               'pathSmtp': pathSmtp})
    else:
        generate_html_Rcommand = '{scirptPath} --script_dir {dirPath} --input_json {jsonPath}\
         --save_dir {savePath} --project_name {project}'.format(**{'scirptPath': pathToRscript,
                                                                 'dirPath': path_to_R_dir,
                                                                 'jsonPath': pathToJson,
                                                                 'savePath': resourceDir,
                                                                 'project': projetcName})

    logger.info(generate_html_Rcommand)
    try:
        subprocess.check_output(generate_html_Rcommand, shell=True)
    except Exception as e:
        logger.error(e)
        logger.error(e.args)
        logger.error(e.message)
        sys.exit("Failed to call Rscript. Check Command to call Rscript")

    path_to_html = '{}/{}-report.html'.format(resourceDir, projetcName)

    return path_to_html
