# -*- coding:utf-8 -*-
__author__ = 'rwang'

import urllib2
import re
import os
import time
import sendmail
import formpage
import jsonpost
import jspost
import htmlparser
import configuration
import logging
import logging.config
import socket
socket.setdefaulttimeout(10.0)

#pip install BeautifulSoup
from BeautifulSoup import BeautifulSoup

#global save_folder, original_folder
#__RETRY_TIMES__ = 3
#__MONITOR_WAITING__ = 60*60*4
__FORM_WAITING_TIME__ = 2
__RESOURCE_FOLDER__ = "resource/"
__FILE_INFO__ = "info.ini"
__FILE_DATA__ = "urls.txt"
__MONITOR__ = 1
__INITIAL__ = 2
__FILTER_PAGE_SUBMIT_KEYS__ = ","
__FILTER_PAGE_SUBMIT_KEY__ = ":"
__DUMMY_PAGE_NUMBER__ = "${PAGENUMBER}$"

__WEBSITE_MODE_HTML__ = 0
__WEBSITE_MODE_SUBMIT__ = 1
__WEBSITE_MODE_JSON_POST__ = 2
__WEBSITE_MODE_JS_POST__ = 3



class grab:
    def __init__(self):
        logging.config.fileConfig("logging.ini")
        self.__logger = logging.getLogger('grab')
        self.__c = configuration.configuration()
        self.__c.fileConfig("configuration.ini")
        self.__RETRY_TIMES__ = int(self.__c.getValue("Runtime","retry_times"))
        self.__f = formpage.formpage()
        self.__h = htmlparser.htmlpaser()
        self.__j = jsonpost.jsonpost()
        self.__js = jspost.jspost()
        self.__taskID = ""

    def __gethrefnameByaTag(self, content, tagName):
        title = ""
        #print content,tagName
        pat = re.compile(r'%s="([^"]*)"' %tagName)
        h = pat.search(str(content))
        if h is not None:
            title = h.group(1)

            #print title.replace("\n"," ")
            title = title.replace("\n"," ")
        #print "h - 1",h
        '''
        pat = re.compile(r'span="([^"]*)"')  #span around the name in title=
        h = pat.search(str(content))
        if h is not None:
            title = h.group(1)
            #print title.replace("\n"," ")
            return title.replace("\n"," ")
        '''
        return title
        #print "h - 2",h

        '''
        contents = str(content).split(kw)
        if len(contents) > 1:
            cutoff = contents[1].split("</a>")[0].split(">")
            if len(cutoff) > 1:
                title = cutoff[1]
        #print "To strip all blank"
        while True: #strip all blank
            if title == title.strip():
                break
            else:
                title = title.strip()
        #print "strip done"
        return title.replace("\n"," ")
        '''

    def __getahrefFromData(self, data):
        data = data.replace("<![endif]-->","")
        return BeautifulSoup(data).findAll('a')

    def __genAbsoluteUrl(self,url,href):
        #print url, href
        #print href.split("/")[-1]
        #print "here:",href.replace(href.split("/")[-1],"")
        url = url.strip("/")
        urls = url.split("/")
        if len(urls) > 1:
            useless = urls[-1]
            url = url.replace(useless,"").strip("/")
        #print url
        if href.startswith("/"):
            return urls[0]+ "//" + urls[2] + href
        else:
            pre = href.replace(href.split("/")[-1],"").strip("/")
            if pre != "" and url.find(pre) != -1: #22,宁夏政府采购公共服务平台-招标公告
                #print "yes"
                url = url.split(pre)[0]
                return url + href
            else:
                return url + "/" + href

    def __cleanClear(self, url):
        return url.strip("/").replace("amp;","")

    def __gethrefnamebydata(self, data, content):

        #data = data.replace("'","").replace('"','').replace("&amp;","&")
        #content = content.replace("'","").replace('"','').replace("&amp;","&")
        data = data.replace("&amp;","&").replace("../","").replace("'","").replace('"','')
        content = content.replace("&amp;","&").replace("../","").replace("'","").replace('"','')

        splitter = content.strip("</a>")
        #print("s-0", splitter)
        splitter = splitter.split(">")[0]

        #print("s-1",splitter)
        if data.find(splitter) == -1:
            self.__logger.warn("The splitter %s in gethrefnamebydata does not work!!!" %splitter)
            self.__saveToFile("filter_debug.txt",[data,splitter],'w')
            return ""
        #print splitter
        name = ""
        try:
            #name = data.split(splitter)[-1].split('<p class="now-link-title l">')[1].split("</p>")[0].strip()

            #print data.split(splitter)[-1]
            #print name
            name = data.split(splitter)[-1]
            #print name
            if name.find('<p class=now-link-title l>') != -1: #13,name = 河北省公共资源交易服务平台
                name = name.split('<p class=now-link-title l>')[1].split("</p>")[0].strip()
                #print name
                #print "2"
            #return
            if name.find('<span class=txt  title=') != -1: #9, name = 招标项目-中国国际招标网
                name = name.split('<span class=txt  title=')[1]
                name = name.split('>')[0]
                #print "3",name

            if name.find('>') != -1:
                name = name.split('>')[1]

            #print name
            if name.find('<') != -1:
                name = name.split('<')[0].strip()
                #print "0",name
            '''
            if name.find('</a') != -1:
                name = name.split('</a')[0].strip()
                print "0",name

            if name.find('</a>') != -1:
                name = name.split('</a>')[0].strip()
                print "1",name
            '''
            '''
            if name.find('<p class="now-link-title l">') != -1: #13,name = 河北省公共资源交易服务平台
                name = name.split('<p class="now-link-title l">')[1].split("</p>")[0].strip()
                print "2",name
            '''
            '''
            if name.find('>') != -1: #13,name = 河北省公共资源交易服务平台
                name = name.split('>')[1]
                print "2",name
            '''

            if name.find('<span>') != -1:
                name = name.split('<span>')[0]
                print "3",name

            '''
            if name.find('<font') != -1: #21 宁夏回族自治区公共资源交易网-工程交易
                name = name.split('<font')[0]
                print "4",name
            '''
            while True:
                name = name.strip()
                if name == name.strip():
                    break
            name = name.replace("\r\n","").replace(" ","").replace("\r","").replace("\n","").replace("\t","")
            #print name
        except Exception,e:
            self.__logger.error(e)
            name = ""
        #print name
        return name

    def __convertDigInCharToNumber(self, char):
        dig = ""
        for c in char:
            if c.isdigit():
                dig += c
            else:
                break
        return int(dig)

    def __saveToFile(self, filename, sList, mode):
        nret = True
        #print filename,sList,mode
        data = ''
        for strUrl in sList:
            #print strUrl
            data = data + strUrl + '\r\n'
        f = open(filename,mode)
        try:
            #print data.strip("\r\n")
            f.write(data.strip("\r\n"))
            #f.write(data)
            f.write('\r\n')
                #print "write file %s successfully" % filename
        except Exception,e:
            self.__logger.error("Exception:" + str(e))
            self.__logger.error("write file %s failed" % filename)
            nret = False
        finally:
            f.close()
        return nret

    def __getListFromFile(self, filename):
        urllist = []
        if os.path.exists(filename) is not True:
            return urllist
        f = open(filename,'r')
        try:
            for line in f.readlines():
                urllist.append(line.strip("\r\n"))
        except Exception,e:
            self.__logger.error("Exception:" + str(e))
            self.__logger.error("read file %s error" %filename)
        finally:
            f.close()
        return urllist

    def __sendReport(self,mailbody="",count=0, mode=""):
        srv = self.__c.getValue("Report","smtpserver")
        port = self.__c.getValue("Report","port")
        sender = self.__c.getValue("Report","sender")
        fromname = self.__c.getValue("Report","from")
        subject = self.__c.getValue("Report","subject")
        subject = str(count) + subject + self.__c.getValue(self.__taskID,"name")
        pwd = self.__c.getValue("Report","password")
        to = self.__c.getValue("Report","to")
        cc = self.__c.getValue("Report","cc")
        attachments = None

        if mode != "" and mode == "debug":
            to = self.__c.getValue("Report", "debug_to")
            subject = mode.upper() + "_" + subject
            attachment = os.getcwd() + "/" + "serverzb.log"
            attachments = [attachment]
        nRet = False
        for i in (0,self.__RETRY_TIMES__):
            nRet = sendmail.sendmail(srv, port, sender, subject, fromname, pwd, to, cc, mailbody, attachments)
            if nRet:
                break
            if i < self.__RETRY_TIMES__:
                self.__logger.debug("RETRY send mail %i" % (i+1))
        if nRet is not True:
            self.__logger.error("Fail to send out email")
        return nRet

    def __genMessage(self, data):
        body_prefix = '<!DOCTYPE html><html><head lang="en"><meta charset="UTF-8"><title></title></head><body>'
        body_suffix = '</body></html>'
        return body_prefix + data + body_suffix

    def __logTimeStamp(self):
        ISOTIMEFORMAT= '%Y-%m-%d %X'
        self.__logger.info(time.strftime(ISOTIMEFORMAT, time.localtime()))

    def __initFolderNFile(self,folders):
        folder_list = folders.split("/")
        folder = ""
        for sub_folder in folder_list:
            folder = folder + sub_folder
            if os.path.exists(folder) is not True:
                os.system("mkdir %s" %folder)
            folder = folder + "/"
        '''
        name = self.__taskID+ "_" + self.__c.getValue(self.__taskID,"name")

        if os.path.exists(__RESOURCE_FOLDER__ + "/" + name) is not True:
            os.system("mkdir %s" %(__RESOURCE_FOLDER__ + "/" + name))
        '''
        c_info = configuration.configuration()
        file_info = folder + __FILE_INFO__
        c_info.fileConfig(file_info)
        url = self.__c.getValue(self.__taskID,"url")
        c_info.setValue("Info","url",self.__genFirstPageUrl(url))
        name = self.__c.getValue(self.__taskID,"name")
        c_info.setValue("Info","name",name)
        ISOTIMEFORMAT= '%Y-%m-%d %X'
        c_info.setValue("Info","timestamp",time.strftime(ISOTIMEFORMAT,time.localtime()))

    def __appendChangeToFile(self,new_url_list,url_file):
        ori_url_list = self.__getListFromFile(url_file)
        temp_file = 'temp.txt'
        if self.__saveToFile(temp_file,new_url_list+ori_url_list,'w') is not True:
            self.__logger.error("failed to save the new target file %s" %temp_file)
            os.system("rm -rf %s" %temp_file)
            return False
        os.system("rm -rf %s" %url_file)
        os.system("mv %s %s" % (temp_file, url_file))
        return True

    def monitor(self, task_id):
        self.__taskID = task_id
        self.__logTimeStamp()
        task_name = {__MONITOR__:"Monitor",__INITIAL__:"Initial"}
        folder = __RESOURCE_FOLDER__  + task_id + "_" + self.__c.getValue(task_id,"name")
        urls_file = folder + "/" + __FILE_DATA__
        info_url_key = self.__c.getValue(task_id,"info_url_key")
        name_tag = self.__c.getValue(task_id,"name_tag")
        url_sample = self.__c.getValue(task_id,"url")
        page_base = self.__genPageBase(int(self.__c.getValue("Runtime","page_base")),int(self.__c.getValue("Runtime","session_interval")))
        #print folder
        #anti_grab_interval = self.__c.getValue(task_id,"anti_grab_interval")
        task_mode = self.__detectTaskMode(folder)
        self.__logger.info("====%s...====" %task_name[task_mode])
        if task_mode == __INITIAL__:
            self.__initFolderNFile(folder)
        iPage = 0
        url_count_per_page = 0
        changed_urls_all = []
        website_mode = self.__detectWebsiteMode(url_sample)
        while True:
            iPage += 1
            if iPage > page_base:
                self.__logger.debug("current page %i is exceed the page_base %i" %(iPage,page_base))
                break
            self.__logger.info("Get page data in page %i"%iPage)
            page_data = self.__getPageData(url_sample,iPage,website_mode)
            if page_data == "":
                self.__logger.error("Fail to get page data")
                break
            #print page_data[0:20]
            l_info_url = self.__retrieveURLs(page_data,info_url_key,name_tag,website_mode)
            #if iPage == 1:
            #    url_count_per_page = len(l_info_url)
            #    self.__logger.debug("url_count_per_page is %i" %url_count_per_page)
            if l_info_url ==[]:
                self.__logger.error("Fail to get info url")
                break
            self.__logger.debug("Get %i info urls" %len(l_info_url))

            changed_urls = self.__compareWithUrlsInfoInDatabase(l_info_url,urls_file)

            if len(changed_urls) == 0:
                self.__logger.debug("There is no changed url any more")
                break
            else:
                self.__appendChangeToFile(changed_urls,urls_file)
                self.__logger.debug("get changed items %i" %len(changed_urls))
                changed_urls_all.extend(changed_urls)
                #if len(changed_urls) < url_count_per_page:
                #    self.__logger.debug("count of changed url %i is less than the count per page %i" %(len(changed_urls),url_count_per_page))
                #    break
            #if anti_grab_interval != "":
            #    time.sleep(int(anti_grab_interval))
        self.__logger.info("===Scanning Done===")
        if changed_urls_all == []:
            self.__logger.info("Nothing changed")
            return
        self.__logger.info("Get %i changes" %(len(changed_urls_all)))
        if task_mode == __MONITOR__:
            self.__logger.info("Notify the changes")
            self.__notifyTheChanges(changed_urls_all)

    def __notifyTheChanges(self,changeList):
        notify = ''
        if changeList == []:
            self.__logger.info("Nothing to notify")
            return
        i = 1
        for line in changeList:
            try:
                notify_line = '<a href=\"' + line.split(";")[1] + '\">' + str(i) + "." +line.split(";")[0] + '</a>'
            except:
                notify_line = ""
            notify = notify + notify_line + '<br>'
            i += 1

        mail_body = self.__genMessage(notify)
        mode = self.__c.getValue("Project","mode")
        debug_info = ""
        if mode.lower() == "debug":
            debug_info = "in debug mode"
        self.__logger.info("Send mail with notify %s %s" %(notify,debug_info))
        if self.__sendReport(mail_body, len(changeList), mode):
            self.__logger.info("Send mail successfully")
        else:
            self.__logger.error("Fail to send mail")

    def __detectTaskMode(self, folder):
        if self.__isExistSection(folder):
            return __MONITOR__
        else:
            return __INITIAL__

    def __isExistSection(self,folder):
        file_ini = r'%s/%s'%(folder,__FILE_INFO__)
        file_data = r'%s/%s'%(folder,__FILE_DATA__)
        return os.path.exists(file_ini) and os.path.exists(file_data)

    def __genFirstPageUrl(self, url):
        if url.find(__DUMMY_PAGE_NUMBER__) != -1:
            return url.replace(__DUMMY_PAGE_NUMBER__, "1")
        else:
            return url

    def __genURLByReplaceKey(self,url_sample,count):
        return url_sample.replace(__DUMMY_PAGE_NUMBER__,str(count))

    def __genURLBySubmit(self,url_sample,count,l_submitter):
        pass

    def __getPageData(self,url,index,mode):
        data = ""
        if mode == __WEBSITE_MODE_HTML__:
            url = url.replace(__DUMMY_PAGE_NUMBER__, str(index))
            data = self.__getPageDataHtml(url)
        elif mode == __WEBSITE_MODE_SUBMIT__:
            l_submit_key = self.__genSubmitKeyList()
            data = self.__getPageDataJS(url,l_submit_key,index)
        elif mode == __WEBSITE_MODE_JSON_POST__:
            post_url = self.__c.getValue(self.__taskID,"post_url")
            post_para = self.__c.getValue(self.__taskID,"post_para")
            post_header = self.__c.getValue(self.__taskID,"post_header")
            per_request = self.__c.getValue(self.__taskID,"per_request")
            if per_request != "":
                per_request = int(per_request)
            else:
                per_request = 0
            data = self.__getPageDataJSONPost(post_url,post_para,post_header,index,per_request)
        elif mode == __WEBSITE_MODE_JS_POST__:
            post_url = self.__c.getValue(self.__taskID,"post_url")
            post_para = self.__c.getValue(self.__taskID,"post_para")
            per_request = int(self.__c.getValue(self.__taskID,"per_request"))
            splitter = self.__c.getValue(self.__taskID,"splitter")
            stripper = self.__c.getValue(self.__taskID,"stripper")
            #target_url = self.__c.getValue(self.__taskID,"target_url")
            data = self.__getPageDataJSPost(post_url,post_para,index,per_request,splitter,stripper)
        return data

    def __getPageDataHtml(self,url):
        return self.__h.getHtmlData(url)
        #return self.__visitUrl(url)

    def __getPageDataJS(self,url,keys, index):
        time.sleep(__FORM_WAITING_TIME__)
        return self.__f.handleForm(url,keys,index)

    def __genSubmitKeyList(self):
        l = []
        s = self.__c.getValue(self.__taskID,"page_submit_keys").split(__FILTER_PAGE_SUBMIT_KEYS__)
        for k in s:
           l.append(k.split(__FILTER_PAGE_SUBMIT_KEY__))
        return l

    def __retrieveURLs(self,data,urlKey,nameTag, mode):
        if mode == __WEBSITE_MODE_HTML__ or mode == __WEBSITE_MODE_SUBMIT__ or mode == __WEBSITE_MODE_JS_POST__:
            return self.__retrieveURLsInfoInPage(data,urlKey,nameTag)
        elif mode == __WEBSITE_MODE_JSON_POST__:
            target_url = self.__c.getValue(self.__taskID,"target_url")
            json_name = self.__c.getValue(self.__taskID,"json_name")
            json_urlid = self.__c.getValue(self.__taskID,"json_urlid")
            #print target_url
            return self.__retrieveURLsByJSONPost(data,json_name,target_url,json_urlid)
        else:
            return []

    def __retrieveURLsInfoInPage(self,data,urlKey,nameTag):
        #print urlKey
        url_list = []
        contents = self.__getahrefFromData(data)
        if contents == []:
            self.__logger.error("Fail to get a href From data")
            return url_list
        #tag = keyword[0]
        #value = keyword[1]
        pat_href = re.compile(r'href="([^"]*)"')
        #pat_tag = re.compile(r'%s="([^"]*)"'%tag)
        pat2 = re.compile(r'http')

        for content in contents:
            h = pat_href.search(str(content))
            if h is None:
                continue
            href = h.group(1)
            if href == "": #There is no url link
                continue
            #print "1",str(content)
            if urlKey != "" and href.find(urlKey) == -1:  #The href url link does not contain the expected words
                #print("href does not contain urlKey")
                #print str(content).find(urlKey)
                if str(content).find(urlKey) == -1:      #The <a> content does not contain the expected words
                    continue
            #name = ""
            #print "2",str(content)
            if nameTag == "title": ##the url name is in href title
                name = self.__gethrefnameByaTag(content, nameTag)
            else:
                name = self.__gethrefnamebydata(data,str(content))
            if name == "":
                continue
                #name = self.__test(content)
            #print href,name
            if pat2.search(href):
                ans = href
            else:
                base_url = self.__genFirstPageUrl(self.__c.getValue(self.__taskID,"url"))
                ans = self.__genAbsoluteUrl(base_url,href)
            ans = self.__cleanClear(ans)
                #print ans
            url_list.append(name+";"+ans)
        return url_list

    def __compareWithUrlsInfoInDatabase(self, src_urls,des_file):
        des_urls = self.__getListFromFile(des_file)
        if des_urls == []:
            #self.__saveToFile(des_file,src_urls,'a')
            return src_urls
        else:
            changed_urls = []
            for src_url in src_urls:
                end = False
                for des_url in des_urls:
                    if des_url == src_url:
                        end = True
                        break
                if end:
                    pass
                else:
                    changed_urls.append(src_url)
            return changed_urls

    def __genPageBase(self,per,during):
        i = int(during/60/60)
        if i == 0:
            hours = 1
        else:
            hours = i
        return per*hours

    def __detectWebsiteMode(self,url):
        if url.find(__DUMMY_PAGE_NUMBER__) != -1:
            return __WEBSITE_MODE_HTML__
        elif self.__c.getValue(self.__taskID,"page_submit_keys") != "":
            return __WEBSITE_MODE_SUBMIT__
        elif self.__c.getValue(self.__taskID,"post_url") != "" and self.__c.getValue(self.__taskID,"post_para") != "" \
                and self.__c.getValue(self.__taskID,"target_url") != "" and self.__c.getValue(self.__taskID,"json_name") != "" \
                and self.__c.getValue(self.__taskID,"json_urlid") != "":
            return __WEBSITE_MODE_JSON_POST__
        elif self.__c.getValue(self.__taskID,"post_url") != "" and self.__c.getValue(self.__taskID,"post_para") != "" \
                and self.__c.getValue(self.__taskID,"info_url_key") != "":
            return __WEBSITE_MODE_JS_POST__
        else:
            return -1

    def __getPageDataJSONPost(self, url,para,header,pageNumber,perRequest):
        #print url
        data = self.__j.jsonRequest(url,para,header,pageNumber,perRequest)
        #print data
        if data == "{}" or data == "[]":
            data = ""
        return data
        #return j.jsonParser(data)

    def __retrieveURLsByJSONPost(self, data,key_name,key_url,url_id):
        return self.__j.jsonParser(data,key_name,key_url,url_id)

    def __getPageDataJSPost(self,url,para,pageIndex,requestNumber,strSplitter,strStripper):
        #print url
        data = self.__js.jsRequest(url,para,pageIndex,requestNumber,strSplitter,strStripper)
        #print data
        return data

    def __retrieveURLsByJSPost(self, data,url_keys):
        return []
        #return self.__j.jsonParser(data,url_keys)

#g = grab()
#g.init_base("Site4")
#g.init_base("Site9")
#g.init_base("Site8")

#nohup python -u zb.py > nohup.out 2>&1 &
