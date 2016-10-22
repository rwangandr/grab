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
    os.system("rm -rf *.log")


    c = configuration.configuration()
    c.fileConfig("configuration.ini")
    mode = c.getValue("Project","mode")

    l = configuration.configuration()
    l.fileConfig("logging.ini")
    if mode.lower() == "debug":
        l.setValue("handler_consoleHandler","level","DEBUG")
        l.setValue("handler_fileHandler","level","DEBUG")
    else:
        l.setValue("handler_consoleHandler","level","INFO")
        l.setValue("handler_fileHandler","level","INFO")
    logging.config.fileConfig("logging.ini")
    logger = logging.getLogger('main')
    g= grab.grab()

    while True:
        sites = c.getValue("Project","sites").split(",")
        for section in sites:
            name = c.getValue(section,"name")
            logger.info("====Task %s,%s===="%(section,name))
            g.monitor(section)
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