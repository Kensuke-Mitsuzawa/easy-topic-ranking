#! /usr/bin/Rscript

library(knitr)
library(markdown)
library(optparse)
library(plyr)
library(tools)

getResultRows <- function(listIndex, topic_cluster_results){
  itemsInList <- topic_cluster_results[[listIndex]]
  wordsItem <- paste(itemsInList$wordsInTopic, collapse = ', ')
  bestSentences <- paste(itemsInList$bestSentences[[1]], collapse = ' || ')
  
  return(data.frame("topicParameter"=itemsInList$topicParameter,
                    "topicId"=itemsInList$topicID,
                    "docs"=itemsInList$docsCluster,
                    "words"=wordsItem,
                    "sentences"=bestSentences))
}


KnitHtml <- function(project_name, save_dir, results_frame){
  path_to_html <- file.path(save_dir, sprintf('%s-report.html', project_name))
  knitr::opts_knit$set(upload.fun=image_uri)
  knitr::knit2html(input = './htmlReport.Rmd', output = path_to_html)
  Sys.chmod(paths = path_to_html, mode = '0777')
  
  return(path_to_html)
}


send_mail_sendmailR <- function(path_to_html, kMailFrom, kMailTo, kSubject){
  library(sendmailR)
  # send html by e-mail
  html_str <- paste(readLines(path_to_html), collapse="\n")
  headers <- list("Content-Type"="text/html", "charset" = "utf-8", "Content-Trensfer-Encoding"="7bit")
  msg <- mime_part(html_str)
  msg[["headers"]][["Content-Type"]] <- "text/html"
  sendmailR::sendmail(from = kMailFrom, to = kMailTo, subject = kSubject, headers = headers, msg = msg)
}


send_mail_mailR <- function(path_to_html, kMailFrom, kMailTo, kSubject){
    library(mailR)
    # these arguments are initialized in parser
    smtp_conf <- list(host.name = host.name, user.name = user.name, passwd = passwd)
    html_str <- paste(readLines(path_to_html), collapse="\n")
    send.mail(from = kMailFrom, 
                     to = kMailTo,
                     subject = kSubject,
                     body = html_str,
                     html = TRUE,
                     smtp = smtp_conf,
                     encoding = 'utf-8',
                     send = TRUE,
                     debug = TRUE)
}


main <- function(script_dir, path_json, save_dir, mailTo, mailFrom, 
                 project_name, flag_send_mail=T, mail_subject='Clustering Result'){
  setwd(script_dir)
  if(file.exists(path_json)==F){
    stop("json file can not be found. System exits")
  }
  topic_cluster_results <- rjson::fromJSON(file = path_json)
  results_frame <- plyr::ldply(.data = 1:length(topic_cluster_results), .fun = getResultRows, topic_cluster_results)
  print (results_frame)
  
  html_path <- KnitHtml(project_name, save_dir, results_frame)
  
  if(flag_send_mail==T){
    send_mail_mailR(html_path, mailFrom, mailTo, mail_subject)
  }
}


exampleUsage <- function(){
  script_dir <- '~/Desktop/analysis_work/topicRanking/Rscripts/'
  path_json <- '../resources/example.json'
  
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
  optparse::make_option(c('-mailfrom', '--email_address_from'), type='character', help=''),
  optparse::make_option(c('-mail', '--email_address'), type='character', help=''),
  optparse::make_option(c('-savedir', '--save_dir'), type='character', help=''),
  optparse::make_option(c('-pname', '--project_name'), type='character'),
  optparse::make_option(c('-stmpconf', '--path_smtp_conf'), type='character'),
  optparse::make_option(c('-sendmail', '--mail_send'), type='logical', action='store_true', default=FALSE, help='')
)
opt <- optparse::parse_args(optparse::OptionParser(option_list=option_list))

if(is.null(opt$script_dir)) stop("--script_dir is mandatory option")
if(is.null(opt$input_json)) stop("--input_json is mandatory option")
if(is.null(opt$project_name)) stop("--project_name is mandatory option")
if(is.null(opt$save_dir)) stop("--save_dir is mandatory option")
if(opt$mail_send==TRUE){
  if(is.null(opt$email_address)) stop("--email_address is mandatory option")
  if(is.null(opt$email_address_from)) stop("--email_address_from is mandatory option")
  if(is.null(opt$path_smtp_conf)) stop("--path_smtp_conf is mandatory option")
  email_address <- opt$email_address
  email_address_from <- opt$email_address_from
  if(file.exists(opt$path_smtp_conf)==F){ stop("file in --path_smtp_conf does not exists") }
  smtp_conf_df <- read.table(tools::file_path_as_absolute(opt$path_smtp_conf), sep = ',', header = T)
  host.name <<- as.character(smtp_conf_df$host.name)
  user.name <<- as.character(smtp_conf_df$user.name)
  passwd <<- as.character(smtp_conf_df$passwd)
} else {
  email_address <- ''
  email_address_from <- ''
}

main(script_dir = opt$script_dir, path_json = opt$input_json, save_dir = opt$save_dir, 
     mailTo = email_address, mailFrom = email_address_from,  
     project_name = opt$project_name, flag_send_mail= opt$mail_send, mail_subject='Clustering Result')
