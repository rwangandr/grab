# -*- coding:utf-8 -*-
__author__ = 'rwang'

import urllib2
import re
import os
import time
import sendmail
import formpage
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
class grab:
    def __init__(self):
        logging.config.fileConfig("logging.ini")
        self.__logger = logging.getLogger('grab')
        self.__c = configuration.configuration()
        self.__c.fileConfig("configuration.ini")
        self.__RETRY_TIMES__ = int(self.__c.getValue("Runtime","retry_times"))
        self.__f = formpage.formpage()

    def __gethrefname(self, content, kw):
        title = ""
        pat = re.compile(r'title="([^"]*)"')
        h = pat.search(str(content))
        if h is not None:
            title = h.group(1)
            #print title.replace("\n"," ")
            return title.replace("\n"," ")

        pat = re.compile(r'span="([^"]*)"')
        h = pat.search(str(content))
        if h is not None:
            title = h.group(1)
            #print title.replace("\n"," ")
            return title.replace("\n"," ")

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

    def __visitUrl(self, url):
        data = ""
        req = urllib2.Request(url)
        try:
            u = urllib2.urlopen(req)
            data = u.read()
        except urllib2.URLError, e:
            pass
            #self.__logger.error(url)
            #self.__logger.error(e.reason)
        finally:
            return data

    def __getahrefFromURL(self, url):
        data = ""
        content = []
        nRetry = False
        for i in range(0, self.__RETRY_TIMES__):
            if nRetry:
                self.__logger.warn("Retry %i" %i)
            data = self.__visitUrl(url)
            if data != "":
                break
            else:
                nRetry = True
        if data != "":
            #print data
            data = data.replace("<![endif]-->","")
            content = BeautifulSoup(data).findAll('a')
        else:
            self.__logger.error("Failed to visit %s" %url)
        #print "content",content
        return content

    def __getOptionTagFromURL(self, url):
        data = ""
        content = []
        nRetry = False
        for i in range(0, self.__RETRY_TIMES__):
            if nRetry:
                self.__logger.warn("Retry %i" %i)
            data = self.__visitUrl(url)
            if data != "":
                break
            else:
                nRetry = True
        if data != "":
            #print data
            data = data.replace("<![endif]-->","")
            content = BeautifulSoup(data).findAll('option')
        else:
            self.__logger.error("Failed to visit %s" %url)
        #print "content",content
        return content

    def __getahrefFromData(self, data):
        data = data.replace("<![endif]-->","")
        return BeautifulSoup(data).findAll('a')

    def __genAbsoluteUrl(self,url,href):
        url = url.strip("/")
        urls = url.split("/")
        if len(urls) > 1:
            useless = urls[-1]
            url = url.replace(useless,"").strip("/")

        if href.startswith("/"):
            return urls[0]+ "//" + urls[2] + href
        else:
            return url + "/" + href

    def __cleanClear(self, url):
        return url.strip("/").replace("amp;","")

    def __gethrefnamebydata(self, data, content):
        #data = data.replace('"','')
        #print data
        #content = content.replace('"','')
        #print content
        splitter = content.strip("</a>").split(">")[0] + ">"
        #splitter = splitter.replace()
        #print splitter
        #print data.split(splitter)[-1].split('<p class=now-link-title l>')[1]
        name = ""
        try:
            name = data.split(splitter)[1].split('<p class="now-link-title l">')[1].split("</p>")[0].strip()
        except:
            pass
        #print name
        return name

    def __retrieveURLsInPage(self,url,data,keyword):
        url_list = []
        #print url,data[0],keyword
        contents = self.__getahrefFromData(data)
        if contents == []:
            self.__logger.error("Fail to get a href From URL %s" %(url))
            return contents
        tag = keyword.split(",")[0]
        value = keyword.split(",")[1]
        pat_href = re.compile(r'href="([^"]*)"')
        pat_tag = re.compile(r'%s="([^"]*)"'%tag)
        pat2 = re.compile(r'http')
        #print contents
        for content in contents:
            h = pat_href.search(str(content))
            if h is None:
                continue
            href = h.group(1)
            t = pat_tag.search(str(content))
            if t is None:
                continue
            tag_data = t.group(1)

            #if ((keyword != "title") and (href.find(keyword) != -1)) or ((keyword == "title") and (str(content).find(keyword) != -1)):
            if tag_data.find(value) != -1 and href != "":
                #print content,href,keyword
                name = self.__gethrefname(content, href)
                if name == "":
                    name = self.__gethrefnamebydata(data,str(content))
                #name = self.__test(content)
                #print href,name
                if pat2.search(href):
                    ans = href
                else:
                    ans = self.__genAbsoluteUrl(url,href)
                ans = self.__cleanClear(ans)
                #print ans
                url_list.append(name+";"+ans)
        return url_list

    def __convertDigInCharToNumber(self, char):
        dig = ""
        for c in char:
            if c.isdigit():
                dig += c
            else:
                break
        return int(dig)

    def __getPageCount(self,url,item,keyword,offsite):
        count = self.__getPageCountByHref(url,item,keyword,offsite)
        if count == 0:
            #print "~~~"
            count = self.__getPageCountByOption(url,item,keyword,offsite)
        #print count
        return count

    def __getPageCountByHref(self,url,item,keyword,offsite):
        count = 0
        contents = self.__getahrefFromURL(url)
        if contents == []:
            self.__logger.error("Fail to get a href From URL %s" %(url))
            return count
        #print contents
        #print item,keyword,offsite
        pat = re.compile(r'%s="([^"]*)"' %item)
        pat2 = re.compile(r'%s' %keyword)
        #print item,keyword

        for content in contents:
            #print content
            h = pat.search(str(content))

            if h is None:
                continue
            href = h.group(1)
            #print href
            if pat2.search(href):
                #print href.split(keyword)[-1],offsite

                count_str = href.split(keyword)[-1].split(",")[int(offsite)-1].strip("(").strip(")").strip("'").strip('"').strip()
                #print count_str
                if count_str[0].isdigit() and count_str.find("/") == -1:
                    #print keyword, href
                    count_temp = self.__convertDigInCharToNumber(count_str)
                else:
                    continue
                if count_temp > count:
                    count = count_temp
        return count

    def __getPageCountByOption(self,url,item,keyword,offsite):
        count = 0
        contents = self.__getOptionTagFromURL(url)
        if contents == []:
            self.__logger.error("Fail to get Option tag From URL %s" %(url))
            return count
        #print contents
        #print item,keyword,offsite
        pat = re.compile(r'%s="([^"]*)"' %item)
        #pat2 = re.compile(r'%s' %keyword)
        #print item,keyword

        for content in contents:
            #print content
            h = pat.search(str(content))

            if h is None:
                continue
            href = h.group(1)
            #print href
            ####if pat2.search(href):
                #print href.split(keyword)[-1],offsite
                ###count_str = href.split(keyword)[-1].split(",")[int(offsite)-1].strip("(").strip(")").strip("'").strip('"').strip()
                #print count_str
            count_temp = self.__convertDigInCharToNumber(href)

            if count_temp > count:
                count = count_temp
        #print count
        return count

    def __getPageDataHtml(self,url):
        return self.__visitUrl(url)

    def __getPageDataJS(self,url,page_submit_key,index):
        time.sleep(__FORM_WAITING_TIME__)
        return self.__f.handleForm(url,page_submit_key,index)

    def __getPageData(self,url,keyword,page_submit_key,index):
        #print url,keyword,page_submit_key,index
        if page_submit_key == "":
            if keyword.find("${pagenumber}$") != -1:
                page_url = url.replace(url.split("/")[-1],keyword.replace("${pagenumber}$",str(index)))
            elif keyword.find("/") != -1:
                page_url = url.split(keyword)[0]+keyword+str(index)+"."+url.split(".")[-1]
            else:
                page_url = url+"&"+keyword+str(index)
            self.__logger.info("Retrieve data from %s" % page_url)
            data = self.__getPageDataHtml(page_url)
            #print "==",data[0],"=="
            #if data == "":
            #    self.__logger.error("Fail to get data from %s",page_url)
            return data
        else:
            return self.__getPageDataJS(url,page_submit_key,index)

    def __saveToFile(self, filename, sList, mode):
        nret = True
        #print filename
        data = ''
        for strUrl in sList:
            #print strUrl
            data = data + strUrl + '\r\n'
        f = open(filename,mode)
        try:
            f.write(data.strip("\r\n"))
            f.write('\r\n')
                #print "write file %s successfully" % filename
        except:
            self.__logger.error("write file %s failed" % filename)
            nret = False

        f.close()
        return nret

    def __getListFromFile(self, filename):
        urllist = []
        f = open(filename,'r')
        try:
            for line in f.readlines():
                urllist.append(line.strip("\r\n"))
                #print "=="+line.strip("\r\n")+"=="
        except:
            self.__logger.error("read file %s error" %filename)
        finally:
            f.close()
        return urllist

    '''
    def __scanPageIndex(self, url):
        lasturl = ''
        last_page_word = self.__c.getValue("runtime","last_page_word")
        urlprefix,count = self.__getPageCount(url,last_page_word)
        #print("urlprefix is %s" % urlprefix)
        if count != -1:
            lasturl = urlprefix + str(count)

        #for i in range(1,count+1):
            urllist.append(urlprefix+str(i))
        #
        return lasturl

    def __saveIndex(self, index_filename, url, folder):
        lasturl = self.__scanPageIndex(url)
        if lasturl == '':
            self.__logger.error("Fail to get the index in the page %s" %url)
                            #time.sleep(60)
            return False

        #indexfile = folder + '/' + 'index.txt'
        indexurllist = [lasturl]
        if self.__saveToFile(index_filename,indexurllist,'w') is not True:
            self.__logger.error("Fail to save the index file %s" %index_filename)
                            #time.sleep(60)
            return False
        return True
    '''
    def __grabChangedData(self,page_count,url,page_count_filters, url_filter,page_submit_key,urls_file):
        items_count = 0
        for i in range(1, page_count+1):
            url_list = []
            self.__logger.info("Get Page Data in Page %i of URL %s" %(i,url))
            html_data = self.__getPageData(url,page_count_filters[1],page_submit_key,i)
            if html_data == "":
                self.__logger.error("Fail to get Page Data in Page %i of URL %s" %(i,url))
                continue
            #self.__logger.info("Scan page %i" %(i))
            currentList = self.__retrieveURLsInPage(url,html_data,url_filter)
            if currentList == []:
                self.__logger.error("Fail to retrieve URLs In Page %i of URL %s" %(i,url))
                continue
            url_list.extend(currentList)

            #self.__logger.info("Scan page %i done, to save the url list to file %s" %(i, urls_file))
            if self.__saveToFile(urls_file,url_list,'a') is not True:
                self.__logger.error("Failed to save the url list to file %s" %urls_file)
                break
            items_count = items_count + len(url_list)
            #time.sleep(1)
        return items_count


    def __initUrl(self, url, folder, page_count_filters,page_submit_key,url_filter):
        ###Handle the Index###

        index_file = folder + '/' + 'info.ini'
        page_count = self.__getPageCount(url,page_count_filters[0],page_count_filters[1],page_count_filters[2])
        if page_count == 0:
            self.__logger.error("Fail to get the page count")
            return False

        if self.__saveToFile(index_file,[""],'w') is not True:
            self.__logger.error("Fail to save the index file in %s" %folder)
            return False

        index_file_c = configuration.configuration()
        index_file_c.fileConfig(index_file)
        index_file_c.setValue("Info","page_count",str(page_count))
        index_file_c.setValue("Info","url",url)
        index_file_c.setValue("Info","name",folder.split("/")[-1])
        ISOTIMEFORMAT= '%Y-%m-%d %X'
        index_file_c.setValue("Info","timestamp",time.strftime(ISOTIMEFORMAT,time.localtime()))

        urls_file = folder + '/' + 'urls.txt'
        items_count = self.__grabChangedData(page_count,url,page_count_filters,url_filter,page_submit_key,urls_file)
            #break

        index_file_c.setValue("Info","items_count",str(items_count))
        return True

    def __sendReport(self,mailbody=""):
        srv = self.__c.getValue("Report","smtpserver")
        port = self.__c.getValue("Report","port")
        sender = self.__c.getValue("Report","sender")
        fromname = self.__c.getValue("Report","from")
        subject = self.__c.getValue("Report","subject")
        pwd = self.__c.getValue("Report","password")
        to = self.__c.getValue("Report","to")
        attachments = None
        mode = self.__c.getValue("Project","mode")
        if mode != "" and mode == "debug":
            to = self.__c.getValue("Report","debug_to")
            subject = mode.upper()
            attachment = os.getcwd() + "/" + "grab.log"
            attachments = [attachment]
        sendmail.sendmail(srv, port, sender, subject, fromname, pwd, to, "", mailbody, attachments)

    def __genMessage(self, data):
        body_prefix = '<!DOCTYPE html><html><head lang="en"><meta charset="UTF-8"><title></title></head><body>'
        body_suffix = '</body></html>'
        return body_prefix + data + body_suffix

    def __setupFolder(self,name):
        os.system("rm -rf %s" %name)
        os.system("mkdir %s" %name)

    def __logTimeStamp(self):
        ISOTIMEFORMAT= '%Y-%m-%d %X'
        self.__logger.info(time.strftime(ISOTIMEFORMAT, time.localtime()))

    def __initFoler(self,folder):
        os.system("rm -rf %s" %folder)
        os.system("mkdir %s" %folder)

    def init_base(self, section):
        self.__logTimeStamp()
        folder = __RESOURCE_FOLDER__ + self.__c.getValue(section,"name")
        root_url = self.__c.getValue(section,"url")
        page_count_filters = self.__c.getValue(section,"page_count_filters")
        page_submit_key = self.__c.getValue(section,"page_submit_key")
        target_url_highlight = self.__c.getValue(section,"target_url_highlight")
        self.__initFoler(folder)
        self.__initUrl(root_url, folder, page_count_filters.split(","),page_submit_key,target_url_highlight)

    def __compareItemChange(self,src_file,des_file):
        src_url_list = self.__getListFromFile(src_file)
        des_url_list = self.__getListFromFile(des_file)
        changed_url_list = []
        end = False
        for src_url in src_url_list:
            for des_url in des_url_list:
                if des_url == src_url:
                    end = True
                    break
            if end:
                break
            else:
                changed_url_list.append(src_url)
        return changed_url_list


    def __appendChangeToFile(self,new_url_list,url_file):
        ori_url_list = self.__getListFromFile(url_file)
        temp_file = 'temp.txt'
        if self.__saveToFile(temp_file,new_url_list+ ori_url_list,'w') is not True:
            self.__logger.error("failed to save the new target file %s" %temp_file)
            os.system("rm -rf %s" %temp_file)
            return False
        os.system("rm -rf %s" %url_file)
        os.system("mv %s %s" % (temp_file, url_file))
        return True

    def __scanUrl(self, url, folder, page_count_filters,page_submit_key,url_filter):
        web_page_count = self.__getPageCount(url,page_count_filters[0],page_count_filters[1],page_count_filters[2])
        if web_page_count == 0:
            self.__logger.error("Fail to get the page count")
            return []

        index_file = folder + '/' + 'info.ini'
        index_file_c = configuration.configuration()
        index_file_c.fileConfig(index_file)
        ISOTIMEFORMAT= '%Y-%m-%d %X'
        index_file_c.setValue("Info","timestamp",time.strftime(ISOTIMEFORMAT, time.localtime()))

        ori_page_count = int(index_file_c.getValue("Info","page_count"))
        page_count = web_page_count - ori_page_count + 1


        urls_file = folder + '/'+ 'urls_temp.txt'
        items_count = self.__grabChangedData(page_count,url,page_count_filters, url_filter,page_submit_key,urls_file)
        if items_count == 0:
            self.__logger.error("Fail to get the changed count")
            return []

        ori_urls_file = folder + '/'+ 'urls.txt'
        changed_url_list = self.__compareItemChange(urls_file,ori_urls_file)
        os.system("rm -rf %s" %urls_file)
        if changed_url_list == []: #get new target url
            return []
        self.__logger.info("Detect %i changes",len(changed_url_list))
        if self.__appendChangeToFile(changed_url_list,ori_urls_file) is not True:
            return []

        items_count = len(self.__getListFromFile(ori_urls_file))
        index_file_c.setValue("Info","page_count",web_page_count)
        index_file_c.setValue("Info","items_count",items_count)

        return changed_url_list

    def monitor(self, section):
        self.__logTimeStamp()
        folder = __RESOURCE_FOLDER__ + self.__c.getValue(section,"name")
        root_url = self.__c.getValue(section,"url")
        page_count_filters = self.__c.getValue(section,"page_count_filters")
        page_submit_key = self.__c.getValue(section,"page_submit_key")
        target_url_highlight = self.__c.getValue(section,"target_url_highlight")

        changed_url_list = self.__scanUrl(root_url, folder, page_count_filters.split(","),page_submit_key,target_url_highlight)
        notify = ''
        for changed_url in changed_url_list:
            notify_line = '<a href=\"' + changed_url.split(";")[1] + '\">' + changed_url.split(";")[0] + '</a>'
            notify = notify + notify_line + '<br>'

        if notify != '':
            mail_body = self.__genMessage(notify)
            self.__logger.info("Send mail with notify %s" %notify)
            self.__sendReport(mail_body)
            self.__logger.info("Send mail done")
        else:
            mode = self.__c.getValue("Project","mode")
            if mode.lower() == "debug":
                self.__logger.info("Send debug log")
                self.__sendReport()
                self.__logger.info("Send debug log done")


#g = grab()
#g.init_base("Site4")
#g.init_base("Site9")
#g.init_base("Site8")

#nohup python -u grab.py > nohup.out 2>&1 &