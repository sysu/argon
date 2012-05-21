class Cacher:

    def __init__(self,prefix=None,cache = global_cache):
        self.cache = cache
        if prefix is not None:
            self.bind(prefix)
        self.dict = []

    def __set__(self,obj,val):
        raise Exception(u'Should never set value to Cacher')

    def __getitem__(self,key):
        return self.dict.get(key)

    def bind(self,prefix):
        self.prefix = prefix

