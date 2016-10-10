# -*- coding:utf-8 -*-
__author__ = 'rwang'

import urllib2
import re
import os
import time
import sendmail
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

class grab:
    def __init__(self):
        logging.config.fileConfig("logging.ini")
        self.__logger = logging.getLogger('grab')
        self.__c = configuration.configuration()
        self.__c.fileConfig("configuration.ini")
        self.__RETRY_TIMES__ = int(self.__c.getValue("Runtime","retry_times"))

    def __gethrefname(self, content, kw):
        title = ""
        contents = content.split(kw)
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
        #print title
        return title

    def __genBaseUrl(self, url):
        return url.split("/")[0] + "//" + url.split("/")[2] + "/"
        #baseurl = url.strip(url.split("/")[len(url.split("/"))-1])

    def __getahref(self, url):
        data = ""
        content = []
        nRetry = False
        for i in range(0, self.__RETRY_TIMES__):
            #print "to visit url %s" %url
            if nRetry:
                self.__logger.warn("Retry %i" %i)
            data = self.__visitUrl(url)
            if data != "":
                break
            else:
                nRetry = True
            #time.sleep(1)
        if data != "":
            content = BeautifulSoup(data).findAll('a')
        else:
            self.__logger.error("Failed to visit %s" %url)
        return data, content

    def __visitUrl(self, url):
        data = ""
        #self.__logger.info("urllib2.Request(url)")
        req = urllib2.Request(url)
        try:
            #self.__logger.info( "urllib2.urlopen")
            u = urllib2.urlopen(req)
            #self.__logger.info( "u.read()")
            data = u.read()
        except urllib2.URLError, e:
            #self.__logger.info( "__logger")
            self.__logger.error(e.reason)
        finally:
            #self.__logger.info( "return")
            return data

    def __retrievePages(self, url,keyword,exceptword):
        urllist = []
        html,content = self.__getahref(url)
        if html == "":
            return []
        pat = re.compile(r'href="([^"]*)"')
        pat2 = re.compile(r'http')
        baseurl = self.__genBaseUrl(url)

        for item in content:
            h = pat.search(str(item))
            if h is None:
                continue
            href = h.group(1)
            name = self.__gethrefname(html, href)
            #print href,name

            if (name != exceptword) and (name.find(keyword) != -1):
                if pat2.search(href):
                    ans = href
                else:
                    ans = baseurl+href
                urllist.append(name+","+ans)
        return urllist

    def __getPageCount(self, url,keyword):
        count = -1
        urlprefix = ""
        html,content = self.__getahref(url)
        if html == "":
            return urlprefix,count

        pat = re.compile(r'href="([^"]*)"')
        pat2 = re.compile(r'http')
        baseurl = self.__genBaseUrl(url)

        for item in content:
            h = pat.search(str(item))
            if h is None:
                continue
            href = h.group(1)
            name = self.__gethrefname(html, href)

            if (name.find(keyword) != -1):
                if pat2.search(href):
                    ans = href
                else:
                    ans = baseurl+href
                count = int(ans.split("=")[-1])
                #print ans
                while True:
                    if ans.find("amp;") != -1:
                        ans = ans.replace("amp;","")
                    else:
                        break
                urlprefix = ans.strip(str(count))
                break

        return urlprefix,count

    def __saveToFile(self, filename, sList, mode):
        nret = True
        #print filename
        data = ''
        for strUrl in sList:
            #print strUrl
            data = data + strUrl + '\r\n'
        f = open(filename,mode)
        try:
            f.write(data)
            f.write('\r\n')
                #print "write file %s successfully" % filename
        except:
            self.__logger.error("write file %s failed" % filename)
            nret = False

        f.close()
        return nret

    def __scanPage(self, url,kw,exkw):
        urllist = self.__retrievePages(url,kw,exkw)
        return urllist

    def __scanLocalFile(self, filename):
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

    def __scanPageIndex(self, url):
        lasturl = ''
        last_page_word = self.__c.getValue("Parameters","index_last")
        urlprefix,count = self.__getPageCount(url,last_page_word)
        #print("urlprefix is %s" % urlprefix)
        if count != -1:
            lasturl = urlprefix + str(count)
        '''
        for i in range(1,count+1):
            urllist.append(urlprefix+str(i))
        '''
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

    def __handleNewMainUrl(self, url, folder, mainkeyword):
        if url == '':
            return False
        subfolder = folder + "/" + url.split(",")[0]
        os.system("mkdir %s" %subfolder)
        #print "__scanPageIndex %s" %url
        indexfile = subfolder + '/' + 'index.txt'

        if self.__saveIndex(indexfile,url.split(",")[1], subfolder) is not True:
            return False

        suburls = self.__scanLocalFile(indexfile)
                #print url,"==",url.split(",")[0],"==",url.split(",")[0].strip(mainkw)
                #print mainkw.decode('utf-8')
                #print url.split(",")[0].decode('utf-8').strip(mainkw.decode('utf-8'))
                #exit(0)
        pageCount = int(suburls[0].split("=")[-1])
        suburllist = []
        kw = url.split(",")[0].decode('utf-8').strip(mainkeyword.decode('utf-8')).encode('utf-8')
        sublocafile = subfolder + '/' + kw + '.txt'
        for i in range(1, pageCount+1):
                    #time.sleep(1)
            suburl =  suburls[0].replace(str(pageCount),str(i))
            exceptkw = url.split(",")[0]
            self.__logger.info("Scan page %s with keyword %s" %(suburl,kw))
            suburllist.extend(self.__scanPage(suburl,kw,exceptkw))
        self.__logger.info("Scan page with keyword %s done, to save the url list to file %s" %(kw,sublocafile))
        if self.__saveToFile(sublocafile,suburllist,'a') is not True:
            self.__logger.error("failed to save the sublocafile %s" %sublocafile)

        return True
                    #finalurls = __scanLocalFile(sublocafile)
                    #print finalurls

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

    def __refreshInterval(self):
        return int(self.__c.getValue("Runtime","interval"))

    def __setupFolder(self,name):
        os.system("rm -rf %s" %name)
        os.system("mkdir %s" %name)

    def __beContinue(self):
        if self.__c.getValue("Runtime","continue").lower() == "no":
            return False
        else:
            return True

    def init_base(self, mainurl,mainkw):
        #mainkw = u"招标"
        #print u"施工招标".strip(u"招标")
        #exit(0)

        #base_url = "http://www.tjconstruct.cn/"
        ISOTIMEFORMAT= '%Y-%m-%d %X'
        self.__logger.info(time.strftime(ISOTIMEFORMAT, time.localtime()))
        self.__logger.info("Scan page %s with keyword %s" % (mainurl,mainkw))

        urllist = self.__scanPage(mainurl,mainkw,"")
        if urllist == []:
            self.__logger.error('In page %s,there is no href contains the keyword %s' % (mainurl,mainkw))
            return False

        self.__setupFolder(mainkw)

        folder = mainkw

        mainlocalfile = folder + '/' + mainkw + '.txt'

        self.__logger.info("Save url list %s to file %s" % (urllist, mainlocalfile))
        if self.__saveToFile(mainlocalfile,urllist,'w') is not True:
            self.__logger.error("Fail to save mainlocalfile %s " % mainlocalfile)
            return False
        self.__logger.info("scan local file %s" % (mainlocalfile))

        localurls = self.__scanLocalFile(mainlocalfile)
        for localurl in localurls:
            #if localurl.find("http://www.tjconstruct.cn/zbxx.aspx?type=glzb") == -1:
            #    continue
            if localurl != "":
                self.__logger.info("Handle new url ==%s==" %localurl)
                self.__handleNewMainUrl(localurl, folder, mainkw)
            else:
                self.__logger.warn("There is a blank line in %s" %mainlocalfile)
        return True

    def monitor(self, mainurl,mainkw):
        #os.system("mkdir %s" %mainkw)
        last_page_word = self.__c.getValue("Parameters","index_last")
        rootfolder = mainkw
        rootfile = mainkw + '/' + mainkw + '.txt'
        if os.path.exists(rootfile) is not True:
            self.__logger.error("There is no file %s,exit" %rootfile)
            return
        while True:
            interval = self.__refreshInterval()
            ISOTIMEFORMAT= '%Y-%m-%d %X'
            self.__logger.info(time.strftime(ISOTIMEFORMAT, time.localtime()))
            self.__logger.info("====Start scan page %s with keyword %s====" % (mainurl,mainkw))
            notify = ''
            urllist = self.__scanPage(mainurl,mainkw,"")
            if urllist == []:
                self.__logger.error('In page %s,there is no href contains the keyword %s' % (mainurl,mainkw))
                time.sleep(interval)
                continue
            original_urllist = self.__scanLocalFile(rootfile)

            for url in urllist:
                self.__logger.info("Detect the sub page %s" %url)
                #print "monitor url is %s" %url
                bNew = False
                for original_url in original_urllist:
                    #print "original url is %s" %original_url
                    if url == original_url:
                        bNew = False
                        break
                    else:
                        bNew = True
                #print bNew
                if bNew:
                    newurllist = [url]
                    if self.__saveToFile(rootfile,newurllist,'a') is not True:
                        self.__logger.error("Error: fail to save rootfile %s " % rootfile)
                        break
                    else:
                        self.__logger.info("New Url %s is detected" %url)
                        self.__handleNewMainUrl(url, rootfolder, mainkw)

            local_urls = self.__scanLocalFile(rootfile)
            for local_url in local_urls:
                if local_url == "":
                    continue
                self.__logger.info("Detect the target url changes in %s" % local_url)
                subfolder = rootfolder + "/" + local_url.split(",")[0]
                indexfile = subfolder + "/" + "index.txt"
                if os.path.exists(indexfile) is not True:
                    self.__logger.error("There is no index file %s" %indexfile)
                    continue
                f = open(indexfile, 'r')
                indexcount = f.readlines()[0].strip("\r\n").split('=')[-1]
                f.close()
                #print("The indexcount is %s" %indexcount)
                urlprefix,count = self.__getPageCount(local_url.split(",")[1],last_page_word)
                #print indexcount,"==",count
                if int(indexcount) != count:
                    self.__logger.info("In Website %s, last page count is changed from %s to %i" %(local_url,indexcount,count))
                    #print "Index is changed"
                    if self.__saveIndex(indexfile, local_url.split(",")[1], subfolder) is not True:
                        self.__logger.error("fail to save index")
                        continue
                kw = local_url.split(",")[0].decode('utf-8').strip(mainkw.decode('utf-8')).encode('utf-8')
                exceptkw = local_url.split(",")[0]
                targetfile = subfolder + "/" + kw + ".txt"
                original_targeturllist = self.__scanLocalFile(targetfile)
                suburllist = []
                for i in range(1, count-int(indexcount)+1+1):
                    self.__logger.info("To scan page %i" %i)
                    suburllist.extend(self.__scanPage(urlprefix + str(i),kw,exceptkw))
                end = False
                newtargeturllist = []
                for suburl in suburllist:
                    for original_targeturl in original_targeturllist:
                        if suburl == original_targeturl:
                            end = True
                            break
                    if end:
                        break
                    else:
                        newtargeturllist.append(suburl)
                        #print(suburl)
                        #newtargeturllist= suburl
                self.__logger.info ("See if there is any new target url")
                if newtargeturllist != []: #get new target url
                    self.__logger.info ("Get new target urls")
                    newfile = subfolder + '/' + kw + 'new.txt'
                    #newfile = "1.txt"
                    targetfile = subfolder + '/' + kw + '.txt'
                    #print newtargeturllist + original_targeturllist
                    #print newtargeturllist
                    #print(newtargeturllist + original_targeturllist)
                    #break
                    if self.__saveToFile(newfile,newtargeturllist+ original_targeturllist,'w') is not True:
                        self.__logger.error("failed to save the new target file %s" %newfile)
                        os.system("rm -rf %s" %newfile)
                        continue
                    os.system("rm -rf %s" %targetfile)
                    os.system("mv %s %s" % (newfile, targetfile))


                    self.__logger.info ("Generate new target url notification")
                    for newtargetur in newtargeturllist:
                        #'<a href="http://www.tjconstruct.cn/shchxt/tonggao.doc/epr_zbgg/2016/ZBGG1604[2016]0913.htm">test</a>'
                        notifyline = '<a href=\"' + newtargetur.split(",")[1] + '\">' + newtargetur.split(",")[0] + '</a>'
                        notify = notify + notifyline + '<br>'
                        #mailbody = mailbody + newtargetur.split(",")[0] + "," + newtargetur.split(",")[1] + "\r\n"
                    #print mailbody

            if notify != '':
                mailbody = self.__genMessage(notify)
                self.__logger.info("Send mail with notify %s" %notify)
                self.__sendReport(mailbody)
                self.__logger.info("Send mail done")
            else:
                mode = self.__c.getValue("Project","mode")
                if mode != "" and mode == "debug":
                    self.__logger.info("Send debug log")
                    self.__sendReport()
                    self.__logger.info("Send debug log done")
            #break
            self.__logger.info("====Finish scan page %s with keyword %s====" % (mainurl,mainkw))
            if self.__beContinue() is not True:
                self.__logger.info("====Time is up, quit====")
                break
            else:
                self.__logger.info("Waiting %i hours for next scan" % (interval/60/60))
                time.sleep(interval)


#nohup python -u grab.py > nohup.out 2>&1 &