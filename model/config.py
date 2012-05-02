# -*- coding: utf-8 -*-
import sys

sys.path.append('../')

"""
    将dbConfig写成类，可以读入配置文件,以后设置argo.conf配置文件, 对所有运行参数进行设置,格式如下：
    [section1]
    name1 = val1
    name1 = val2
    [section2]
    name1 = val1
    ...

    ie:
    [database]
    host=localhost
    port=3306
    ...

    运行sever时，格式 ./server -c argo.conf

    目前暂时hard code

"""


class baseConfig(object):
    """
        提供读入配置文件功能
    """
    def __init__(self, configfile = "argo.conf"):
        self.conf = configfile;

class dbConfig(baseConfig):

    def __init__(self):
        """ Read config from argo.conf, section database
            Temporary hard code
        """
        # self.host= "172.18.42.164"
        self.host = "localhost"
        self.port= 3306
        self.user= "bbs"
        self.passwd= "forargo"
        self.dbname = "argo"
