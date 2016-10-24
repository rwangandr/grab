#  -*- coding:utf-8 -*-
__author__ = 'rwang'

import urllib
import urllib2
import json
import logging
import logging.config
import configuration
import time
import htmlparser
__DUMMY_START__ = "${START}$"
__DUMMY_END__ = "${END}$"

class jspost:
    def __init__(self):
        logging.config.fileConfig("logging.ini")
        self.__logger = logging.getLogger('jspost')
        c = configuration.configuration()
        c.fileConfig("configuration.ini")
        self.__RETRY_TIMES__ = int(c.getValue("Runtime","retry_times"))
        self.__PAGE_INTERVAL__ = int(c.getValue("Runtime","page_interval"))
        self.__h = htmlparser.htmlpaser()

    def __http_post(self,url,para):
        #jdata = json.dumps(values)             # 对数据进行JSON格式化编码
        #print jdata
        strResult = ""
        tried = 1
        #print url
        #print para
        req = urllib2.Request(url, para)
        while True:
            try:
                response = urllib2.urlopen(req,timeout=30)
                strResult = response.read()
                break
            #except urllib2.URLError,e:
            except Exception,e:
                self.__logger.error(e)
                tried += 1
                if tried > self.__RETRY_TIMES__:
                    self.__logger.error("Fail to visit url %s" %url)
                    break
                time.sleep(self.__PAGE_INTERVAL__)
                self.__logger.warn("Retry %i" %tried)
        return strResult

    def __parseDataList(self,data_list,strName,url_sample,urlID):
        #url_sample = "http://www.hnsggzy.com/web/detailview.htm?id=${CONTENTID}$"
        urls = []
        #lstName = strName.split(",")
        for data in data_list:
            #print data["TAGS"]
            #print data["CONTENTID"]
            #print data["CONTENTTITLE"]
            '''
            targetName = ""
            for i in range(0,len(lstName)):
                targetName += "_" + data[lstName[i]]
            targetName = targetName.strip("_")
            '''
            targetName = data[strName]
            #targetName = self.__h.convertToU(targetName)
            url = url_sample.replace("${URLID}$",data[urlID])
            urls.append((targetName + "," + url).encode('utf-8'))
            #urls.append(targetName.encode('utf-8'))
        return urls

    def jsRequest(self, url, requestPara, pageIndex,requestNumber,splitter,stripper):
        istart = (pageIndex-1)*requestNumber + 1
        iend = istart + requestNumber - 1
        resp = self.__http_post(url.replace(__DUMMY_START__,str(istart)).replace(__DUMMY_END__,str(iend)), requestPara)
        html_data = self.__respFormat(resp,splitter,stripper)
        return html_data

    def __respFormat(self, data, splitter, stripper):
        prefix = "<!DOCTYPE html><html><head lang='en'><meta charset='UTF-8'><title></title></head><body>"
        suffix = "</body></html>"
        format_data = ""
        html_data = ""
        sub_datas = data.split(splitter)
        for i in range(1, len(sub_datas)):
            sub_data = sub_datas[i].strip(stripper)
            #data = data.split(splitter)[-1].strip(stripper)
            sub_data = sub_data.replace("\\'","'").replace('"',"'").replace("title='<!--articletitle-->'","")
            format_data += sub_data + "<br>"
        html_data = prefix + format_data + suffix
        return html_data

