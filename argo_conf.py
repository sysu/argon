# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
    argo 的全局配置文件
'''

class ConfigDB:
    '''
        Database config
    '''
    # host= "10.42.43.1"
    host = "localhost"
    port= 3306
    user= "bbs"
    passwd= "forargo"
    dbname = "argo"

class ConfigCache:
    '''
        Cache config
    '''
    # host = '10.42.43.1'
    host = "localhost"
    port = 6379


#class ConfigTelnetServer:
#   pass


#class ConfigWebServer:
#   pass

