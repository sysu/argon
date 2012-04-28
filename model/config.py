import MySQLdb

class dbConfig(object):

    def __init__(self):
        """ Read config from argo.conf, section database
            Temporary hard code
        """
        self.host= "localhost"
        self.port= 3306
        self.user= "bbs"
        self.passwd= "forargo"
        self.dbname = "argo"


