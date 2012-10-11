import tornado.web
from lib import BaseHandler, manager

class BoardHandler(BaseHandler):

    def get(self, boardname, rank=None):
        board = manager.board.get_board(boardname)
        if not board:
            raise tornado.web.HTTPError(404)
        boardname = board.boardname
        maxrank = max(0, manager.post.get_post_total(board['bid']) - 3)
        if rank is not None:
            rank = int(rank)
            posts = manager.post.get_posts(board['bid'], rank, 30)
        elif self.get_current_user() :
            userid = self.get_current_user()
            lastread = manager.readmark.get_first_read(userid, boardname) or 0
            lastread = manager.post.prev_three_post(board.bid, lastread) or 0
            posts = manager.post.get_posts_after_pid(
                board.bid, lastread, 30)
            rank = manager.post.get_rank_num(board.bid, lastread)
        else:
            rank = maxrank
            posts = manager.post.get_posts(board['bid'], rank, 30)
        if self.get_current_user() :
            userid = self.get_current_user()
            manager.readmark.wrapper_post_with_readmark(posts, boardname, userid)
        vistors = (
            ("LTaoist", "2012-03-04"),
            ("gcc", "2012-01-09"),
            ("cypress", "2012-01-01"),
            )
        board['bm'] = board['bm'] and board['bm'].split(':')
        board['httpbg'] = "http://ww3.sinaimg.cn/large/6b888227jw1dwesulldlyj.jpg"
        self.srender('board.html', board=board, rank=rank, maxrank=maxrank,
                     posts=posts, vistors=vistors)
