class RedisElementBase:

    def __init__(self,name,prefix='',update=None):
        if prefix :
            self.name = prefix + name
        else :
            self.name = name
        if update :
            self.update(update)

    def bind(self,cache):
        self.cache = cache

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s[%s]' % (self.__class__.__name__,self.name)

    def dump(self):
        return self.cache.dump(self.name)

    def exists(self):
        return self.cache.exists(self.name)

    def ttl(self):
        return self.cache.ttl(self.name)

    def type(self):
        return self.cache.type(self.name)

    def restore(self,ttl,dump_val):
        return self.cache.restore(self.name,ttl,dump_val)

    def expire(self,sec):
        return self.cache.expire(self.name,sec)

    def expire_p(self,millsec):
        return self.cache.pexpire(self.name,millsec)

    def expireat(self,time):
        return self.cache.expireat(self.name,time)

    def expireat_p(self,milltime):
        return self.cache.pexpireat(self.name,time)
    
class RedisDict(RedisElementBase):

    def __repr__(self):
        return 'RedisHashes[%s]' % self.name

    def set(self,key,value):
        return self.cache.hset(self.name,key,value)

    __setitem__ = set
    
    def get(self,key):
        return self.cache.hget(self.name,key)

    __getitem__ = get

    def delete(self,key):
        return self.cache.hdel(self.name,key)

    __delitem__ = delete

    def inc(self,key,inc=1):
        return self.cache.hincrby(self.name,key)

    def mget(self,*fields):
        return self.cache.hmget(self.name,fields)

    def values(self):
        return self.cache.hvals(self.name)

    def exists(self,key):
        return self.cache.hexists(self.name,key)

    __contains__ = exists

    def update(self,dic):
        return self.cache.hmset(self.name,dic)

    def keys(self):
        return self.cache.hkeys(self.name)

    def all(self):
        return self.cache.hgetall(self.name)

    def len(self):
        return self.cache.hlen(self.name)

    __len__ = len

    def set_nx(self,key,value):
        return self.cache.hsetnx(self.name,key,value)

    def __iter__(self):
        return iter(self.all())

class RedisSet:

    def add(self,*mem):
        return self.cache.sadd(mems)

    update = add

    def intersect(self,*othersets):
        return self.cache.sinter( (self.name,) + othersets )

    def move(self,otherset,mem):
        return self.cache.smove(self.name,otherset,mem)

    def union(self,*othersets):
        return self.cache.sunion( (self.name,) + othersets)

    def card(self):
        return self.cache.scard(self.name)

    __len__ = card

    def intersect_s(self,*sets):
        return self.cache.sinterstore(self.name,othersets)

    def pop(self):
        return self.cache.spop(self.name)

    def union_s(self,*sets):
        return self.cache.sunionstore(self.name,othersets)

    def diff(self,*othersets):
        return self.cache.sdiff( (self.name,) + othersets)

    def ismember(self,mem):
        return self.cache.sismember(self.name,mem)

    __contains__ = ismember
        
    def random(self):
        return self.cache.srandmember(self.name)

    def diff_s(self,*othersets):
        return self.cache.sdiffstore(self.name,othersets)

    def all(self):
        return self.cache.smembers(self.name)

    def remove(self,*mems):
        return self.cache.srem(self.name,mems)

    def __iter__(self):
        return iter(self.all())
