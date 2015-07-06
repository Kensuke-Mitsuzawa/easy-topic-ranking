library(knitr)
library(markdown)
library(sendmailR)
library(optparse)
library(plyr)


getResultRows <- function(listIndex, topic_cluster_results){
  itemsInList <- topic_cluster_results[[listIndex]]
  wordsItem <- paste(itemsInList$wordsInTopic, collapse = ', ')
  
  return(data.frame("topicParameter"=itemsInList$topicParameter,
                    "topicId"=itemsInList$topicID,
                    "docs"=itemsInList$docsCluster,
                    "words"=wordsItem))
}


KnitHtml <- function(project_name, save_dir){
  path_to_html <- file.path(save_dir, sprintf('%s-report.html', project_name))
  knitr::opts_knit$set(upload.fun=image_uri)
  knitr::knit2html(input = './htmlReport.Rmd', output = path_to_html)
  Sys.chmod(paths = path_to_html, mode = '0777')
  
  return(path_to_html)
}


send_mail <- function(path_to_html, kMailFrom, kMailTo, kSubject){
  # send html by e-mail
  html_str <- paste(readLines(path_to_html),collapse="\n")
  headers <- list(`Content-Type`="text/html; charset = \"utf-8\"", `Content-Trensfer-Encoding`="7bit")
  msg <- mime_part(html_str)
  msg[["headers"]][["Content-Type"]] <- "text/html"
  sendmailR::sendmail(from = kMailFrom, to = kMailTo, subject = kSubject, headers = headers, msg = msg)
}


main <- function(script_dir, path_json, save_dir, mailTo, mailFrom, 
                 project_name, flag_send_mail=T, mail_subject='Clustering Result'){
  setwd(script_dir)
  topic_cluster_results <- rjson::fromJSON(file = path_json)
  results_frame <- plyr::ldply(.data = 1:length(topic_cluster_results), .fun = getResultRows, topic_cluster_results)
  
  html_path <- KnitHtml(project_name, save_dir)
  
  if(flag_send_mail==T){
    send_mail(html_path, mailFrom, mailTo, kSubject)
  }
}


exampleUsage <- function(){
  script_dir <- '~/Desktop/analysis_work/sandbox/topicRanking/Rscripts/'
  path_json <- '../resources/exampleOut.json'
  
  flag_send_mail <- F
  mailFrom <- 'hoge'
  mailTo <- 'hoge'
  
  projectName <- 'testExample'
  save_dir <- '../resources/'
  
  main(script_dir = script_dir, path_json = path_json, save_dir = save_dir, 
       mailTo = mailTo, mailFrom = mailFrom, project_name = projectName, flag_send_mail = flag_send_mail)
}


option_list <- list(
  optparse::make_option(c('-spath', '--script_dir'), type='character', help=''),
  optparse::make_option(c('-ipath', '--input_json'), type='character', help=''),
  optparse::make_option(c('-mail', '--email_address'), type='character', help=''),
  optparse::make_option(c('-pname', '--project_name'), type='character'),
  optparse::make_option(c('-sendmail', '--mail_send'), type='logical', default=FALSE, help='')
  )

