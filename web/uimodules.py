from lib import manager, url_for_avatar, bid_wrapper, timeformat
import tornado.web

class BoardSet(tornado.web.UIModule):

    def render(self, boards):
        return self.render_string("ui/boardset.html", boards=boards)

class UserBox(tornado.web.UIModule):

    def render(self, userid):
        if userid is not None:
            userfav = map(bid_wrapper(userid),
                          manager.favourite.get_all(userid))
            return self.render_string(
                "ui/userbox.html", userid=userid,
                url_for_avatar=url_for_avatar(userid),
                userfav=userfav)
        else:
            return self.render_string("ui/userbox.html", userid=userid)

class Carousel(tornado.web.UIModule):

    def render(self, htmlid, content):
        if content is None:
            return ''
        return self.render_string("ui/carousel.html", htmlid=htmlid,
                                  content=content)

class PostTable(tornado.web.UIModule):

    def render(self, postlist):
        return self.render_string("ui/posttable.html", postlist=postlist,
                                  timeformat=timeformat)

class TopicTable(tornado.web.UIModule):

    def render(self, topiclist):
        return self.render_string("ui/topictable.html", topiclist=topiclist,
                                  timeformat=timeformat)

