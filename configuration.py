__author__ = 'carl'

import ConfigParser
import commands


# FILE_FOLDER = commands.getoutput("echo $BEMAILPATH") + "config/"

class configuration:
    def __init__(self):
        self.__conFile = None

    def fileConfig(self, filename):
        self.__conFile = filename

    def getValue(self, section, field):
        if self.__conFile == None:
            return ''
        config = ConfigParser.ConfigParser()
        config.read(self.__conFile)
        if not config.has_option(section, field):
            return ''
        value = config.get(section, field)
        return value

    def setValue(self, section, field, value):
        if self.__conFile == None:
            return False
        config = ConfigParser.ConfigParser()
        config.read(self.__conFile)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, field, value)
        f = open(self.__conFile, 'w+')
        config.write(f)
        f.close
        return True
