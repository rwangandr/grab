__author__ = 'rwang'

import re,urllib2,bs4
import chardet
import socket
socket.setdefaulttimeout(10.0)
import logging
import logging.config
import configuration
import time

class htmlpaser:
    def __init__(self):
        logging.config.fileConfig("logging.ini")
        self.__logger = logging.getLogger('htmlparser')
        c = configuration.configuration()
        c.fileConfig("configuration.ini")
        self.__RETRY_TIMES__ = int(c.getValue("Runtime","retry_times"))
        self.__PAGE_INTERVAL__ = int(c.getValue("Runtime","page_interval"))

    def stripHtmlTag(self,data):
        dr = re.compile(r'<[^>]+>',re.S)
        dd = dr.sub('',data)
        #print(dd)
        return dd

    def getHtmlData(self, url):
        data = ""
        req = urllib2.Request(url)
        tried = 1
        while True:
            try:
                response = urllib2.urlopen(req,timeout=30)
                data = response.read()
                break
            except Exception,e:
                self.__logger.error(e)
                tried += 1
                if tried > self.__RETRY_TIMES__:
                    self.__logger.error("Fail to visit url %s" %url)
                    break
                time.sleep(self.__PAGE_INTERVAL__)
                self.__logger.warn("Retry %i" %tried)
        if data != "":
            data = self.cleanClear(data)
            data = self.convertToU(data)
        return data

    def cleanClear(self, data):
        return data.replace("<![endif]-->","")

    def convertToU(self, data):
        coder = self.__getCharset(data)
        #print coder
        if coder == "utf-8":
            pass
        elif coder == "GB2312":
            data = data.decode("gbk")
        else:
            data = data.decode(coder)
            data = data.encode('utf-8')
        return data

    def lookFor(self, html_data,tag,key):
        #"meta","charset"
        #print html_data
        contents = bs4.BeautifulSoup(html_data,"html.parser").findAll(tag)
        for content in contents:
            #print content
            pat = re.compile(r'%s="([^"]*)"' %key)
            h = pat.search(str(content))
            if h is not None:
                title = h.group(1)
                #print title.replace("\n"," ")
                return title.replace("\n"," ")

    def __getCharset(self, data):
        chardit = chardet.detect(data)
        return chardit['encoding']
