# -*- coding:utf-8 -*-
__author__ = 'rwang'
from BeautifulSoup import BeautifulSoup
import urllib2
import re
import os,time

def gethrefname(content, kw):
    title = ""
    contents = content.split(kw)
    if len(contents) > 1:
        cutoff = contents[1].split("</a>")[0].split(">")
        if len(cutoff) > 1:
            title = cutoff[1]
    while True:
        if title == title.strip():
            break
        else:
            title = title.strip()

    #print title
    return title

def savepage(ans, name):
    file_object = open(save_folder + "/" +name+".htm","w")
    try:
        html = urllib2.urlopen(ans).read()
        file_object.write(html)
    except:
        print "Open url error or write file error"
    finally:
         file_object.close( )

def grabHref(url,keyword, exceptword, localfile, level):
    nResult = False
    try:
        html = urllib2.urlopen(url).read()
    except:
        return nResult
    #html = unicode(html,'gb2312','ignore').encode('utf-8','ignore')
    #print html
    '''
    file_object = open('test.html')
    try:
         html = file_object.read( )
    finally:
         file_object.close( )
    '''
    content = BeautifulSoup(html).findAll('a')
    if content == []:
        return nResult
    myfile = open(localfile,'w')
    pat = re.compile(r'href="([^"]*)"')
    pat2 = re.compile(r'http')
    level = level+1
    for item in content:
        h = pat.search(str(item))
        if h is None:
            continue
        href = h.group(1)
        name = gethrefname(html, href)
        print href,name
        #continue


        if pat2.search(href):
            ans = href
        else:
            ans = base_url+href

        if name == "尾页":
            page_num_all = int(href.split("page=")[1])
            for i in range(2,page_num_all):
                scanPage(base_url+href.replace(href.split("page=")[1], str(i)),keyword,name, 1)
            continue
        #keyword = "招标"

        if (name != exceptword) and (name.find(keyword) != -1):
            print "=====Start======"
            #print "exceptword is %s" %exceptword
            #print "Search for keyword %s...." %keyword, "\n", name
            print ans
            print "=====End======"
            subkeyword = name.split(keyword)[0] # 公路招标,施工招标...
            if subkeyword != name and ans != "":
                if scanPage(ans,subkeyword,name, level) is not True:
                    savepage(ans, name)
            '''
            name2 = name.split("招标")[0]

            if name.find(name2) != -1:
                print "招标条目-1!!!!\n", name
                print ans
            '''
            myfile.write(ans)
            myfile.write('\r\n')
        #print ans
    #level = original_level
    myfile.close()
    nResult = True
    return nResult


def scanPage(url,kw, exceptword,level):
    global save_folder, original_folder
    #print level, kw, exceptword, save_folder
    localfile = ""
    if level == 0:
        save_folder = kw
        original_folder = save_folder
        os.system("mkdir %s" %save_folder)
        localfile = save_folder + '/' + kw + '.txt'
    elif level == 1:
        save_folder =original_folder +'/' + kw
        os.system("mkdir %s" %save_folder)
        localfile = save_folder + '/' + kw + '.txt'
    elif level == 2:
        localfile = save_folder+ '/' + kw + '.txt'
    print localfile
    return grabHref(url,kw, exceptword, localfile, level)

