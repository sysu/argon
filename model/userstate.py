from bases import Model,Cacher

class UserState(Model):

    g_online = Cacher('people_online')

    @classmethod
    def total_online(cls):
        return cls.g_online.scard()

    @classmethod
    def login(cls,userid):
        cls.g_online.sadd(userid)

    @classmethod
    def logout(cls,userid):
        cls.g_online.srem(userid)

