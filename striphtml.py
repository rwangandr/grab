# -*- coding:utf-8 -*-
__author__ = 'rwang'
import re
from BeautifulSoup import BeautifulSoup

def stripHtml(data):

    dr = re.compile(r'<[^>]+>',re.S)
    dd = dr.sub('',data)
    #print(dd)
    findLine(dd)

def findLine(data):
    if data.find("招标备案号") != -1:
        print data.strip("\r\n")

def getHtmlData(data):
    data = data.replace("<![endif]-->","")
    contents = BeautifulSoup(data).findAll('a')
    #print contents
    return contents

def parseHtmlData(dataList):
    #pat = re.compile(r'class="([^"]*)"')
    #pat2 = re.compile(r'http')
    #print(dataList)
    for data in dataList:
        print data
        '''
        h = pat.search(str(data))
        if h is None:
            continue
        span = h.group(1)
        if span.find(keyword) != -1:
            print span
            #if pat2.search(span):
            #    ans = span
        '''

if __name__ == '__main__':
    f = open("test.html")
    #f = open("gs.html")

    data = f.read()
    contents = getHtmlData(data)
    parseHtmlData(contents[2])
    parseHtmlData(contents[3])
    #print contents[3],contents[4]

    #for content in contents:
    #    parseHtmlData(content,"title")

    '''
    while True:
        line = f.readline()
        if line and line.strip("\r\n") != "":
            stripHtml(line.strip("\r\n"))
        else:
            break
    '''
    f.close()

