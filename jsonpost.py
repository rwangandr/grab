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
__DUMMY_PAGE_NUMBER__ = "${PAGENUMBER}$"
__DUMMY_START__ = "${START}$"
__DUMMY_END__ = "${END}$"

class jsonpost:
    def __init__(self):
        logging.config.fileConfig("logging.ini")
        self.__logger = logging.getLogger('jsonpost')
        c = configuration.configuration()
        c.fileConfig("configuration.ini")
        self.__RETRY_TIMES__ = int(c.getValue("Runtime","retry_times"))
        self.__PAGE_INTERVAL__ = int(c.getValue("Runtime","page_interval"))
        self.__h = htmlparser.htmlpaser()

    def __http_post(self,url,para,header):
        #jdata = json.dumps(values)             # 对数据进行JSON格式化编码
        #print jdata
        strResult = "{}"
        tried = 1
        req = urllib2.Request(url, para)
        if header != "":
            req.add_header(header.split(",")[0],header.split(",")[1])
        while True:
            try:
                response = urllib2.urlopen(req)
                strResult = response.read()
                break
            except urllib2.URLError,e:
                self.__logger.error(e.reason)
                tried = tried + 1
                if tried > self.__RETRY_TIMES__:
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
            urls.append((targetName.strip() + ";" + url).encode('utf-8'))
            #urls.append(targetName.encode('utf-8'))
        return urls

    def jsonRequest(self, url, requestPara, requestHeader, pageNumber, perRequest=0):
        if perRequest == 0:
            resp = self.__http_post(url, requestPara.replace(__DUMMY_PAGE_NUMBER__,str(pageNumber)),requestHeader)
        else:
            dataStart = (pageNumber-1)*perRequest + 1
            dataEnd = dataStart + perRequest -1
            resp = self.__http_post(url, requestPara.replace(__DUMMY_START__,str(dataStart)).replace(__DUMMY_END__,str(dataEnd)),requestHeader)
        return resp

    def jsonParser(self,strData,strName,url_sample,url_id):
        zb_urls = []
        #print strData
        if strData == "{}" or strData == "[]" or strData == "":
            self.__logger.error("response is empty")
            return zb_urls
        #print json.loads(resp)
        #print strData[0]
        if strData[0] == "{":
            dataList = json.loads(strData)["rows"]
            zb_urls = self.__parseDataList(dataList,strName,url_sample,url_id)
        elif strData[0] == "[":
            zb_urls = self.__validateJson(strData,strName,url_sample,url_id)
        return zb_urls

    def __validateJson(self, strData,tagName,urlSample,tagUrl):
        strData = strData.strip("[").strip("]")
        dataList = strData.split("},{")
        urls = []
        for data in dataList:
            target_name = ""
            url = ""
            data = data.strip("{").strip("}")
            for ddd in data.split(","):
                dd = ddd.split(":")
                if dd[0].find(tagName) != -1:
                    target_name = dd[1].strip("'").strip('"').strip()
                elif dd[0].find(tagUrl) != -1:
                    url = dd[1].strip("'").strip('"')
            if target_name != "" and url != "":
                target_url = urlSample.replace("${URLID}$",url)

                urls.append((target_name + ";" + target_url))
        return urls




'''
url = "http://www.hnsggzy.com/sysquery/query.htm"
request_sample = "code=CMS_GetPublishContentByCode&page=${PAGENUMBER}$&pagesize=18&sortname=istop+desc%2CPublishTime+desc&usePager=true&where=%7B%22op%22%3A%22and%22%2C%22rules%22%3A%5B%7B%22op%22%3A%22like%22%2C%22field%22%3A%22CATEGORYFULLCODE%22%2C%22value%22%3A%22ggfw_jygk%22%2C%22type%22%3A%22string%22%7D%5D%7D"


j = jsonpost()
data = j.jsonRequest(url, request_sample,1)
j.jsonParser(data)
'''
'''
{
    "code": "CMS_GetPublishContentByCode",
    "page": "1",
    "pagesize": "18",
    "sortname": "istop desc,PublishTime desc",
    "usePager": "true",
    "where": {"op":"and","rules":[{"op":"like","field":"CATEGORYFULLCODE","value":"ggfw_jygk","type":"string"}]}
}
'''
#{"code":"CMS_GetPublishContentByCode","page":"1","pagesize":"18","sortname":"istop desc,PublishTime desc","usePager":"true","where":{"op":"and","rules":[{"op":"like","field":"CATEGORYFULLCODE","value":"ggfw_jygk","type":"string"}]}}

'''
    {
    "code": "CMS_GetPublishContentByCode",
    "page": 1,
    "pagesize": 18,
    "sortname": "istopdesc,PublishTimedesc",
    "usePager": true,
    "where": {
        "op": "and",
        "rules": [
            {
                "op": "like",
                "field": "CATEGORYFULLCODE",
                "value": "jygkszgcjszbgg",
                "type": "string"
            }
        ]
    }
}
'''

'''

[{xxlyID:"1",Area:1,GCBH:"KM2016101096",GCMC:"云南省邮电学校“校安工程”排危改扩建（一期）工程监理项目",XMBH:"ZKM2016101096",XMMC:"云南省邮电学校“校安工程”排危改扩建（一期）工程监理项目",GCLB:1,ZBFS:1,ZSType:1,ZBGG_FBQSSJ:"2016-10-19 14:58:00.000",ZBGG_FBJSSJ:"2016-10-25 17:00:00.000",FBZT:null,GGBT:"云南省邮电学校“校安工程”排危改扩建（一期）工程监理项目招标公告",ZBGGGuid:"caba8c40-6ef8-41b2-909f-b0aa90930442",TBJZSJ:"2016-11-11 09:30:00.000",ZBTypeId:null,ZBGG_CreateTime:"2016-10-17 12:10:02.147",BD:"",BDBH:"",BDMC:"",SubSystemName:"JSGC",XXLB:1,BDZBTypeId:",2,",ISBG:0,BGGGBT:"",bgZBGGGuid:"cbf63841-a060-4dcd-b3c8-6de55a97a29e",BGFBQSSJ:"2016-10-19 14:58:00.000",BGFBJSSJ:"2016-10-25 17:00:00.000",PublishTime:"2016-10-19 14:58:00.000",ZTGGType:0,IsNew:1,IsZBZ:1,XXFBGuid:"caba8c40-6ef8-41b2-909f-b0aa90930442",FBKSSJ:"2016-10-19 14:58:00.000",BDGCBH:"KM2016101096",BDMCGGBT:"云南省邮电学校“校安工程”排危改扩建（一期）工程监理项目招标公告",ZTGGTypeText:"",RecordUID:1,RecordsCount:8251},
 {xxlyID:"1",Area:1,GCBH:"KM2016090910(2)",GCMC:"昆明桥隧管理有限公司隧道供电系统整改及不间断电源整体检修维护及电池更换项目",XMBH:"ZKM2016090910",XMMC:"昆明桥隧管理有限公司隧道供电系统整改及不间断电源整体检修维护及电池更换项目",GCLB:9,ZBFS:1,ZSType:1,ZBGG_FBQSSJ:"2016-10-19 14:57:00.000",ZBGG_FBJSSJ:"2016-10-25 17:00:00.000",FBZT:null,GGBT:"昆明桥隧管理有限公司隧道供电系统整改及不间断电源整体检修维护及电池更换项目（第二次公告）",ZBGGGuid:"e3beef8b-1f58-4cd5-ab34-db4120adff4c",TBJZSJ:"2016-11-11 10:30:00.000",ZBTypeId:null,ZBGG_CreateTime:"2016-10-18 16:11:13.497",BD:"",BDBH:"",BDMC:"",SubSystemName:"JSGC",XXLB:1,BDZBTypeId:",7,",ISBG:0,BGGGBT:"",bgZBGGGuid:"7a152e48-a270-4a8e-9532-3c456121b512",BGFBQSSJ:"2016-10-19 14:57:00.000",BGFBJSSJ:"2016-10-25 17:00:00.000",PublishTime:"2016-10-19 14:57:00.000",ZTGGType:0,IsNew:1,IsZBZ:1,XXFBGuid:"e3beef8b-1f58-4cd5-ab34-db4120adff4c",FBKSSJ:"2016-10-19 14:57:00.000",BDGCBH:"KM2016090910(2)",BDMCGGBT:"昆明桥隧管理有限公司隧道供电系统整改及不间断电源整体检修维护及电池更换项目（第二次公告）",ZTGGTypeText:"",RecordUID:2,RecordsCount:8251}]
'''