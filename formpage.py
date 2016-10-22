__author__ = 'rwang'
# -*- coding:utf-8 -*-

import ssl
import monkey_ssl
ssl.wrap_socket = monkey_ssl.getssl()
import mechanize
import cookielib
import time
import logging
import logging.config
import configuration
import htmlparser

class formpage:
    def __init__(self):
        #self.__pageinfo = ""
        # Browser
        self.__br = mechanize.Browser()
        self.__br_i = mechanize.Browser()

        #self.__br = mechanize.urlopen("https://taobao.com")

        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        self.__br.set_cookiejar(cj)
        self.__br_i.set_cookiejar(cj)

        # Browser options
        self.__br.set_handle_equiv(True)
        self.__br.set_handle_gzip(True)
        self.__br.set_handle_redirect(True)
        self.__br.set_handle_referer(True)
        self.__br.set_handle_robots(False)

        # Browser options
        self.__br_i.set_handle_equiv(True)
        self.__br_i.set_handle_gzip(True)
        self.__br_i.set_handle_redirect(True)
        self.__br_i.set_handle_referer(True)
        self.__br_i.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        self.__br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Follows refresh 0 but not hangs on refresh > 0
        self.__br_i.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)

        # User-Agent (this is cheating, ok?)
        self.__br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        self.__br_i.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        logging.config.fileConfig("logging.ini")
        self.__logger = logging.getLogger('formpage')
        c = configuration.configuration()
        c.fileConfig("configuration.ini")
        self.__RETRY_TIMES__ = int(c.getValue("Runtime","retry_times"))
        self.__PAGE_INTERVAL__ = int(c.getValue("Runtime","page_interval"))

        self.__h = htmlparser.htmlpaser()

    def __submit(self):
        page_data = ""
        tried = 1
        while True:
            try:
                self.__br.submit()
                page_data = self.__br.response().read()
                break
            except Exception,e:
                self.__logger.error("Exception:" + str(e))
                tried = tried + 1
                if tried > self.__RETRY_TIMES__:
                    return page_data
                time.sleep(self.__PAGE_INTERVAL__)
                self.__logger.warn("Retry %i" %tried)

        page_data = self.__h.cleanClear(page_data)
        page_data = self.__h.convertToU(page_data)
        return page_data

    def __handleControlText(self, form, control):
        print self.__br
        print control.name
        # name=None, type=None, kind=None, id=None,predicate=None, nr=None,label=None
        #form.find_control(control.name, control.type, None, control.id, None, None, None)
        form.find_control(control.name).readonly = False
        self.__br[control.name] = str("")
        form.find_control(control.name).readonly = True

    def __handleControl(self, form, control, page_keys,page_index):
        nCtl = False
        if control.name is None:
            return nCtl
        #print control.name, page_keys, page_index
        #print form.find_control(control.name).readonly
        form.find_control(control.name).readonly = False
        #print "set readonly as false done"
        page_key_count = len(page_keys)
        #print page_keys,page_index

        for i in range(0,page_key_count):
            key_name = page_keys[i][0]
            if control.name == key_name:
                nCtl = True
                if page_keys[i][1] != "":
                    data = page_keys[i][1]
                else:
                    data = str(page_index)
                self.__br[control.name] = str(data)
                break
                #print control.name,data
        form.find_control(control.name).readonly = True
        return nCtl

    def __fillForm(self,form,page_keys,page_index):
        for control in self.__br.form.controls:
            if control.type == "hidden" or control.type == "text" or control.type == "textarea":
                self.__handleControl(form, control, page_keys,page_index)

            #elif
             #       self.__handleControlText(form, control)

    def handleForm(self,url,l_submitter,index):
        page_data = ""
        tried = 1
        fs = []
        while True:
            try:
                self.__br.open(url)
                fs = self.__br.forms()
                break
            except Exception,e:
                self.__logger.error("Exception:" + str(e))
                tried = tried + 1
                if tried > self.__RETRY_TIMES__:
                    return page_data
                time.sleep(self.__PAGE_INTERVAL__)

        keys = l_submitter
        key = keys[0][0]
        i = -1
        #print "fs",fs
        for f in fs:
            i += 1
            if str(f).find(key) != -1:
                self.__br.select_form(nr=i)
                self.__fillForm(f,keys,index)
                page_data = self.__submit()
                break
        return page_data


#f = formpage()
#page_submit_key = "__EVENTTARGET:MoreInfoList1$Pager,__EVENTARGUMENT:"
#print f.handleForm("http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002001/002001002/MoreInfo.aspx?CategoryNum=002001002",page_submit_key,2)

#page_submit_key = "currentPage:"
#print f.handleForm("http://www.chinabidding.com/search/proj.htm",page_submit_key,2)
