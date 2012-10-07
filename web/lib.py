from model import manager
from datetime import datetime
import tornado

class SDict(dict):

    def __getattr__(self, name):
        return self[name]

def url_for_avatar(userid):
    return "/static/img/avatar/%s" % userid

func = SDict([
    ("url_for_avatar", url_for_avatar),
    ])

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def ch(self):
        return self.application.ch

    @property
    def headers(self):
        return self.application.headers

    def get_current_user(self):
        return self.get_secure_cookie('userid')

    def srender(self, tpl, **kwargs):
        return self.render(tpl, func=func, **kwargs)

def import_handler(modulename, classname):
    module = __import__(name=modulename, fromlist=classname, level=0)
    return getattr(module, classname)

def bid_wrapper(userid):
    def wrapper(bid):
        board = manager.board.get_board_by_id(bid)
        board['is_new'] = manager.readmark.is_new_board(userid, bid,
                                                        board.boardname)
        return board
    return wrapper

def timeformat(time):
    return time.strftime("%d-%m")
