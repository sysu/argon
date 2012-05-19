from base import Model

class User(Model):

    tablename = 'argo_user'

    def __setitem__(self,key,value):
        if key == 'passwd' :
            value = self.crypt(value)
        super(User,self).__setitem__(self,key,value)

    def check_passwd(self,passwd):
        return self.crypt(passwd) == self['passwd']:

    @classmethod
    def check_user_exist(cls,userid):
        res = self.db.query("SELECT userid FROM %s WHERE userid = %s",self.tablename,userid)
        return len(res) == 0

    @classmethod
    def get_user_auth(cls,userid,passwd):
        passwd = self.crypt(passwd)
        res = self.db.get("SELECT * FROM %s WHERE userid = %s, passwd = %s",self.table,self.sql_value(userid),self.sql_value(passwd))
        return res

