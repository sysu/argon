import tornado.web
from lib import BaseHandler, manager

class BoardHandler(BaseHandler):

    def get(self, boardname, rank=None):
        board = manager.board.get_board(boardname)
        if not board:
            raise tornado.web.HTTPError(404)
        boardname = board['boardname']
        maxrank = max(0, manager.post.get_post_total(board['bid']) - 30)
        if (rank is None) or (rank > maxrank):
            rank = maxrank
        posts = manager.post.get_posts(board['bid'], rank, 30)
        vistors = (
            ("LTaoist", "2012-03-04"),
            ("gcc", "2012-01-09"),
            ("cypress", "2012-01-01"),
            )
        board['bm'] = board['bm'] and board['bm'].split(':')
        board['httpbg'] = "http://ww3.sinaimg.cn/large/6b888227jw1dwesulldlyj.jpg"
        self.srender('board.html', board=board, rank=rank, maxrank=maxrank,
                     posts=posts, vistors=vistors)
