#!/usr/bin/env python
import sys
sys.path.append('..')

import tornado.web
from model import manager
from comm.urls import mark,BaseHandler

@mark('MobileIndexHandler')
class MobileIndexHandler(BaseHandler):
    
    def get(self):
        self.render('mobile/m_index.html', top=[], **self.tpl_setting)  

   
@mark('MobileLoginHandler')
class MobileLoginHandler(BaseHandler):

    def get(self):
        self.render('mobile/m_login.html', ref='', **self.tpl_setting)


@mark('MobileBoardHandler')
class MobileBoardHandler(BaseHandler):

    def get(self):
        sections = manager.section.get_all_section()
        for s in sections:
            s['boards'] = manager.board.get_by_sid(s.sid)

        self.render('mobile/m_board.html', sections=sections, **self.tpl_setting)


@mark('MobileDataHandler')
class MobileDataHandler(BaseHandler):

    def get(self):
        self.render('mobile/m_data.html', **self.tpl_setting)


@mark('MobileAboutHandler')
class MobileAboutHandler(BaseHandler):

    def get(self):
        self.render('mobile/m_about.html', **self.tpl_setting)





