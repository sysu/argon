from lib import BaseHandler, manager

class PostHandler(BaseHandler):

    def get(self, pid):
        post = manager.post.get_post(pid)
        if not post:
            raise tornado.web.HTTPError(404)
        board = manager.board.get_board_by_id(post['bid'])
        if post.replyid :
            parent = manager.post.get_post(post.replyid)
            root = manager.post.get_post(post.tid)
            firstpid = root.pid
        else:
            parent = root = None
            firstpid = post.pid
        children = manager.post.get_post_by_replyid(post.pid)
        prevpid = manager.post.prev_post_pid(post.bid, post.pid)
        nextpid = manager.post.next_post_pid(post.bid, post.pid)
        lastpid = manager.post.get_last_pid(post.tid)
        self.srender('post.html', board=board, post=post,
                     parent=parent, root=root, children=children,
                     firstpid=firstpid, prevpid=prevpid,
                     nextpid=nextpid, lastpid=lastpid)
