__author__ = 'rwang'
import grab
import configuration
import logging
import logging.config
import os

if __name__ == '__main__':
    os.system("rm -rf grab.log")
    logging.config.fileConfig("logging.ini")
    logger = logging.getLogger('main')
    g= grab.grab()
    c = configuration.configuration()
    c.fileConfig("configuration.ini")
    url = c.getValue("Parameters","entry")
    keyword = c.getValue("Parameters","keyword")
    type = c.getValue("Project","type")
    if type.lower() == "monitor":
        logger.info("Monitor the website %s with keyword %s" %(url,keyword))
        g.monitor(url,keyword)
    elif type.lower() == "initial":
        logger.info("Initialize the data in website %s with keyword %s" %(url,keyword))
        g.init_base(url,keyword)
    else:
        logger.error("Please double check the config file, the type should be either monitor or initial")
