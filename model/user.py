from bases import IdModel
import bcrypt

class User(IdModel):

    __idname__ = 'uid'
    __ = 'argo_user'
    
    @staticmethod
    def crypt(key):
        d = bcrypt.hashpw(key, bcrypt.gensalt())
        print d
        return d

    @staticmethod
    def match_passwd(val, code):
        return bcrypt.hashpw(val, code) == code
                             
    def set_passwd(self,passwd):
        self['passwd'] = self.crypt(passwd)

    @classmethod
    def check_user_exist(cls,userid):
        return bool(cls.db.get("SELECT userid WHERE userid = %s", userid))

    @classmethod
    def check_user_passwd(cls,userid,passwd):
        res = cls.db.get("SELECT passwd FROM %s WHERE userid = %%s" %\
                             cls.__,
                         userid)
        return res and cls.match_passwd(passwd,res['passwd'])

    @classmethod
    def get_user_auth(cls,userid,passwd):
        if cls.check_user_passwd(userid,passwd):
            return cls.get(cls.get_uid_by_userid(userid))
        else :
            return None

    @classmethod
    def get_uid_by_userid(cls,userid):
        d = cls.db.get("SELECT uid FROM %s WHERE userid = %%s" % cls.__,
                       userid)
        return d and d['uid']

    @classmethod
    def add_user(cls,userid,passwd):
        c = cls(userid=userid)
        c.set_passwd(passwd)
        c.save()
