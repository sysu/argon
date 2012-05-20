from base import Model

class User(Model):

    tablename = 'argo_user'

    def check_passwd(self,passwd):
        return self.crypt(passwd) == self['passwd']

    def set_passwd(self,passwd):
        self['passwd'] = self.crypt(passwd)

    @classmethod
    def check_user_exist(cls,userid):
        res = self.select(cls.tablename,"userid","userid = %s" % userid)
        return len(res) == 0

    @classmethod
    def get_user_auth(cls,userid,passwd):
        passwd = self.crypt(passwd)
        res = self.get(cls.tablename,'*',
                       "userid = %s, passwd = %s" % (userid,passwd))
        return cls(**res)

    @classmethod
    def get_by_userid(cls,userid):
        return self.get(self.tablename,'*','userid = %s' % userid)

    @classmethod
    def get_by_uid(cls,uid):
        return self.get(self.tablename,'*','uid = %s' % uid)

