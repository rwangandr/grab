__author__ = 'rwang'
import grab
import configuration
import logging
import logging.config
import os
import time
__RESOURCE_FOLDER__ = "resource/"

def beContinue():
    if c.getValue("Runtime","continue").lower() == "no":
        return False
    else:
        return True

def isExistSection(name):
    name1 = "info.ini"
    name2 = "urls.txt"
    filename1 = r'%s%s/%s'%(__RESOURCE_FOLDER__,name,name1)
    filename2 = r'%s%s/%s'%(__RESOURCE_FOLDER__,name,name2)
    #print filename
    return os.path.exists(filename1) and os.path.exists(filename2)

def refreshInterval():
    return int(c.getValue("Runtime","session_interval"))

def convertTimeShow(ori_time):
    if ori_time/60 >= 1: #Mins
        if ori_time/60/60 >= 1: #Hour
            if ori_time/60/60/24 >= 1: #Day
                return ori_time/60/60/24,"Day"
            else:
                return ori_time/60/60,"Hour"
        else:
            return ori_time/60,"Minute"
    else:
        return ori_time,"Second"

if __name__ == '__main__':
    os.system("rm -rf grab.log")
    logging.config.fileConfig("logging.ini")
    logger = logging.getLogger('main')
    g= grab.grab()

    c = configuration.configuration()
    c.fileConfig("configuration.ini")

    while True:
        sites = c.getValue("Project","sites").split(",")
        for section in sites:
            name = c.getValue(section,"name")
            if isExistSection(name):
                logger.info("====Start Monitoring Job of Section %s====" %section)
                g.monitor(section)
            else:
                logger.info("====Start Initial Job of Section %s====" %section)
                g.init_base(section)
            logger.info("====Finish Job of section %s====" %section)
        if beContinue() is not True:
            logger.info("====Time is up, quit====")
            break
        else:
            interval = refreshInterval()
            show_time, unit = convertTimeShow(interval)
            if show_time > 1:
                unit = unit + "s"
            logger.info("Waiting %i %s for next scan" % (show_time, unit))
            time.sleep(interval)