import codecs
import re

FILEDBPATH = 'filedb/%s'

class FileDatabase:

    re_comment = re.compile('^ *#.*\n', re.M)

    def __init__(self, prefix):
        self.prefix = prefix

    def append_to_file(self, key, value):
        with codecs.open(self.prefix%key, "a", encoding="utf8") as f:
            f.write('%s\n' % value)

    def get_text(self, key):
        with codecs.open(self.prefix%key, encoding="utf8") as f:
            return f.read()

    def get_clean_text(self, key):
        return self.re_comment.sub('', self.get_text(key))

    def get_list(self, key):
        text = self.get_clean_text(key)
        return filter(None, text.split('\n'))

    def set_text(self, key, value):
        with codecs.open(self.prefix%key, "w", encoding="utf8") as f:
            f.write(value)

filedb = FileDatabase(FILEDBPATH)

append_filedb = filedb.append_to_file
get_text_filedb = filedb.get_text
get_list_filedb = filedb.get_list
set_text_filedb = filedb.set_text
get_clean_text_filedb = filedb.get_clean_text
