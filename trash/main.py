# -*- coding:utf-8 -*-
__author__ = 'rwang'


import os
import os.path
import logging
import logging.config
#import urllib
import urllib2
from bs4 import BeautifulSoup
import sys
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
'''
#sys.path.append("/Users/rwang/Documents/Work/Automation/code/bmam")

from publiclib import myglobal
from publiclib import configuration
from publiclib import database
from publiclib import sshconnect
'''

class grab:
#    __JENKINS_USER = "bemailauto"
#    __JENKINS_PWD = "123@qazsew"
    _logger = None
    #__config = None
    #__PRE_BUILD_SECTION = "Integration_"

    #def __init__(self):
        #logging.config.fileConfig(myglobal.LOGGINGINI)
        #self._logger = logging.getLogger('testserver')
        #self.__config = configuration.configuration()
        #self.__config.fileConfig(myglobal.CONFIGURATONINI)


#http://192.168.22.205/jenkins/view/BeMail/job/BeMail_iOS/200/changes
#[Integration_BMX]
#version = 44
#buildurl = http://192.168.22.205:8080/jenkins/job/BeMail_Proxy_Dev/44/
#buildname = rps-1.0.0.44.war
    '''
    def __readCLUrl(self, component):
        sectionName = self.__PRE_BUILD_SECTION + component.upper()
        jenkins_url = self.__config.getValue(sectionName, "buildurl")
        return jenkins_url + "changes"

    def __readBuildNumber(self, component):
        sectionName = self.__PRE_BUILD_SECTION + component.upper()
        jenkins_version = self.__config.getValue(sectionName, "version")
        return jenkins_version
    '''


#<a href="/jenkins/job/BeMail_Notification_Server_Notifications/134/pollingLog">
    def __stripLastWords(self,ori_url):
        print "get it, ori_url is %s" %ori_url
        tmp_urls = ori_url.split('/')
        new_url = ''
        for i in range(0, len(tmp_urls) - 1):
            #print new_url
            new_url = new_url + tmp_urls[i] + '/'
        print "__stripLastWords return %s" %new_url
        return new_url




    def __getUpStreamUrl(self, jenkins_url, project, build):
        import urllib
        u = urllib.urlopen(jenkins_url)
        soup = BeautifulSoup(u, "html.parser")
        scm_url = ""
        #print jenkins_url
        for a in soup.find_all('a'):
            if a.get("href") != None and (a.get("href").find(project + '/' + build) != -1):
                scm_url = a.get("href")
                #print "get it, scm_url is %s" %scm_url
                break
        tmp_urls = jenkins_url.split('/')
        #url = tmp_urls[0] + "//" + tmp_urls[2] + "/" + self.__stripLastWords(scm_url)
        url = tmp_urls[0] + "//" + tmp_urls[2] + scm_url
        #print "__getUpStreamUrl is %s" %url
        return url

    def getInfo(self, url):
        import re
        tmp = "1.html"
        os.system("curl %s > %s" % (url, tmp))
        f = open(tmp, 'r')
        html= f.read()
        dr = re.compile(r'<[^>]+>',re.S)

        dd = dr.sub(' ',html)
        print dd
        dds = dd.split(' ')
        build_number = ''
        project_name = ''
        for i in range(0, len(dds)-1):
            #print dds[i]
            '''
            if dds[i] == "project":
                project_name = dds[i+2]
            if dds[i] == "number":
                build_number = dds[i+2]
                break
            '''
        #print project_name, build_number
        os.system("rm %s" % tmp)
        return project_name, build_number

    def getlinks(self, url):
        import urllib
        rt = False
        #url = url + "changes"
        u = urllib.urlopen(url)
        #print u
        soup = BeautifulSoup(u, "html.parser")
        #commits = []
        zhaobiaos_url = []
        n = 0
        for a in soup.find_all('a'):
            if a.get("href") != None:
                print a.get("href")
                '''
                if a.get("href").find(u"招标".encode('utf-8')) != -1:
                    zhaobiaos_url.append(a.get("href"))
                    url = a.get("href")
                    urls = url.split('/')
                    commit = urls[len(urls) - 1]
                    #commits.append(commit)
                '''
        return zhaobiaos_url




    def fetch_links(self,furl,burl,stag,etag):
        import urllib2, re
        '''''
        抓取网页新闻
        @param furl 抓取网页地址
        @param burl 网页链接的baseurl,比如凤凰网的链接:<a href="/news/guoji/dir?cid=14&amp;mid=7sdLRL">国际</a>, 根据baseurl可返回<a href="http://i.ifeng.com/news/guoji/dir?cid=14&amp;mid=7sdLRL">国际</a>
        @param stag 抓取网页链接的开始标签
        @param etag 抓取网页链接的结束标签
        @return 加了baseurl的链接列表
        说明: 正则表达式中 '.*?', 采用非贪婪模式匹配多个字符
        '''
        req = urllib2.Request(furl)
        fd = urllib2.urlopen(req)
        content = fd.read()
        fd.close()
        links = []

        import re
        relink = '<a href=(.*)>(.*)</a>'
        relink = '<a href=(.*)>(.*)\n'
        relink = 'htm(.*)'
        info = '<a href="http://www.baidu.com">baidu</a>'
        cinfo = re.findall(relink,content)
        for j in cinfo:
            print j


        m = re.findall(stag+'.*?'+etag,content)

        for j in m:
            #print(j)
            k = j.replace('<a href="', '<a href="'+burl)
            #print(k)
            links.append(k)


        return links

    def fetch_info(self, slink, kw):
        #print slink
        a = slink.strip("</a>").split(">")
        if len(a) > 1:
            b = a[1]
            #print b
            return True

if __name__ == '__main__':
    g = grab()
    #g.getlinks("http://www.tjconstruct.cn/zbxx.aspx")
    #g.getlinks("http://www.tjconstruct.cn/zbxx.aspx")
    #exit(0)
    aList = g.fetch_links("http://www.tjconstruct.cn/zbxx.aspx","http://www.tjconstruct.cn/","<a", "</a>")
    #for a in aList:
    #    g.fetch_info(a, "招标")


#test.getlinks("http://www.tjconstruct.cn/zbxx.aspx")
#test.getInfo("http://www.tjconstruct.cn/zbxx.aspx")
#g.test("http://www.tjconstruct.cn/zbxx.aspx")
'''
<a href='shchxt/tonggao.doc/new/../epr_zbgg/2016/ZBGG2004[2016]0910.htm' class="a09" target="_blank">
                                            （施工）空客A330项目周边道路绿化提升改造工程
                                        </a>

<a href="zbxx.aspx?type=sgzb" class="a02">施工招标</a>
'''


