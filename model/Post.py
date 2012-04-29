from Model import Model

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

class Post(object):

    def __init__(self, row = None):
        # Attrs from argo_posthead.sql
        self.attr_list =['pid','bid','owner','realowner','title','flag','tid','replyid','posttime','attachidx','fromaddr','fromhost','content','quote','signature','agree','disagree']

        if row != None:
            for i in range(0, len(row)):
                setattr(self, self.attr_list[i], row[i])
        self.dict = {}

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            pass

    def __setitem__(self, name, value):
        self.dict[name] = value


    def dump_attr(self):
        attrs = [att for att in self.attr_list if hasattr(self, att)]
        vals = ["'"+str(getattr(self, att))+"'" for att in attrs]
        return  attrs,vals


