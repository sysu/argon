"""
    `pid` int(11) unsigned NOT NULL auto_increment,
    `bid` int(11) unsigned NOT NULL,
    `owner` varchar(14),
    `realowner` varchar(14),
    `title` varchar(60),
    `flag` int(11)  unsigned default 0,
    `tid` int(11) unsigned default 0,
    `replyid` int(11) unsigned,
    `posttime` int(11) unsigned,
    `attachidx` varchar(20),

    `fromaddr` varchar(64),
    `fromhost` varchar(40) NOT NULL,

    `content` text,
    `quote` text,
    `signature` text,

    `agree` int(11) unsigned NOT NULL default 0,
    `disagree` int(11) unsigned NOT NULL default 0,

"""
"""
    Because __setattr__ will cause inf recursion, use an alternative method.
    Remembe to change the post_att_list if argo_filehead has been changed.
"""

post_attr_list = ['pid','bid','owner','realowner','title','flag','tid','replyid','posttime','attachidx','fromaddr','fromhost','content','quote','signature','agree','disagree']

class Post(object):

    def __init__(self, dict = {}):
        self.attr_list = post_attr_list
        for k,v in dict.items():
            if v != None:
                setattr(self, k, v)

    def __getitem__(self, name):
        if hasattr(self,name):
            return getattr(self, name)
        else:
            return None

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def dump_attr(self):
        return [(k, getattr(self,k)) for k in self.attr_list if hasattr(self,k)]


