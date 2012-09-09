class OrderDict(dict):

    def __unicode__(self):
        return 'OrderDict(%s)' % unicode(self._tuple)

    def __str__(self):
        return 'OrderDict(%s)' % unicode(self._tuple)

    def __init__(self, *args, **kwargs):
        super(OrderDict, self).__init__(*args, **kwargs)
        self._tuple = []
        self._froze = False

    def __setitem__(self, key, value):
        if self._froze:
            raise TypeError("'OrderDcit' object does not support "
                            "item assignment after sorted")
        super(OrderDict, self).__setitem__(key, value)

    def keys(self):
        try:
            return self._keys
        except AttributeError:
            raise TypeError("'OrderDcit' cannot get keys before sorted")

    def values(self):
        try:
            return self._values
        except AttributeError:
            raise TypeError("'OrderDcit' cannot get values before sorted")

    def sort(self, cmp=None, key=None, reverse=False):
        self._tuple = self.items()
        self._tuple.sort(cmp=cmp, key=key, reverse=reverse)
        self.__keys__, self.__values__ = zip(*self._tuple)
        self._froze = True

    def tuple(self):
        try:
            return self._tuple
        except AttributeError:
            raise TypeError("'OrderDcit' cannot get tuple before sorted")

    def __iter__(self):
        return self._tuple.__iter__()

def load_boards(all_boards):
    boards = {}
    boards['board'] = OrderDict( (b['boardname'], b) for b in all_boards )
    boards['board'].sort(key=lambda x:x[1]['bid'])
    sections = boards['sections'] = {}
    for b in all_boards :
        if b['sid'] not in sections:
            sections[b['sid']] = OrderDict()
        sections[b['sid']][b['boardname']] = b
    for key in sections:
        sections[key].sort(lambda x:x[1]['bid'])
    return boards, sections

def cache_manage():
    all_boards = manager.board.get_all_boards()
    manager.telnet['board'], manager.telnet['sections'] = load_boards(all_boards)

