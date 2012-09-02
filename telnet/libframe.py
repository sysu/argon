#!/usr/bin/python2
# -*- coding: utf-8 -*-

from datetime import datetime
import functools
import re

from chaofeng import Frame
from chaofeng.g import mark
import chaofeng.ascii as ac
from chaofeng.ui import TextEditor, FinitePagedTable, Animation, ColMenu,\
    NullValueError, SimpleTextBox, TableLoadNoDataError, TextEditorAreaMixIn
import config
from template import env
from model import manager
from libformat import telnet2style

class BaseFrame(Frame):

    u'''
    全部类的基类。
    '''

    _jinja_env = env
    def render_str(self, filename, **kwargs):
        t = self._jinja_env.get_template(filename)
        s = t.render(session=self.session,
                     uwidth=self.format_width,
                     **kwargs)
        return s

    def format_str(self, f, *args):
        return f % args

    def format_width(self,source,width):
        assert isinstance(source, unicode)
        s = source.encode('gbk')
        return ('%*s' % (width, s)).decode('gbk')

    def cls(self):
        u'''
        Clear current screen.
        '''
        self.write(ac.clear)

    def readline(self, buf_size=20):
        u'''
        Read one line.
        '''
        buf = []
        while True :
            ds = self.read_secret()
            for d in ds :
                if d in ac.ks_delete:
                    if buf:
                        buf.pop()
                        self.write(ac.backspace)
                        continue
                elif d in ac.ks_finish :
                    return u''.join(buf)
                elif d == ac.k_ctrl_c:
                    return False
                elif (len(buf) < buf_size) and d.isalnum():
                    buf.append(d)
                    self.write(d)
        return u''.join(buf)                        

    def render(self, filename, **kwargs):
        self.push(self.render_str(filename, **kwargs))

class BaseAuthedFrame(BaseFrame):
    
    def place(self):
        return config.mark2zhname.get(self.__mark__) or u''

    def top_bar(self):
        if self.session['lastboard'] :
            right = u'%s区 [%s]' % (self.session['lastsection'],
                                    self.session['lastboard'])
        else:
            right = u''
        if manager.notify.check_mail_notify(self.userid):
            tpl = 'top_notify'
        elif manager.notify.check_notice_notify(self.userid):
            tpl = 'top_notify_notice'
        else :
            tpl = 'top'
        self.render(tpl, left=self.place(), right=right)

    # def write(self, data):
    #     super(BaseFrame, self).write(self.read())
    #     super(BaseFrame, self).write(data)

    def get_pipe(self):
        return self.session[u'_$$pipe$$']

    def set_pipe(self, value):
        self.session[u'_$$pipe$$'] = value

    def post_bug(self):
        self.suspend('post_bug')

    pipe = property(get_pipe, set_pipe)

    @property
    def user(self):
        u'''
        Alias for self.session.user
        '''
        return self.session.user

    @property
    def userid(self):
        u'''
        Alias for self.session.user.userid
        '''
        return self.session.user.userid

    @property
    def seid(self):
        u'''
        Alias for self.session.user.seid
        '''
        return self.session.user.seid

    @property
    def stack(self):
        u'''
        Alias for self.session.stack, which
        used to record the goto history and
        restore.
        '''
        return self.session.stack

    @property
    def history(self):
        return self.session.history

    ##############################
    #    do something common     #
    ##############################

    # Status Control

    def suspend(self,where,**kwargs):
        u'''
        Push current frame's status to history
        and goto a new frame.
        '''
        self.session.stack.append(self)
        # self.session.history.append(self)
        self.goto(where,**kwargs)

    def goto_back(self):
        u'''
        Go back to previous frame save in
        history.
        '''
        # self.session.history.append(self)
        if self.session.stack:
            self.wakeup(self.session.stack.pop())

    def goto_back_nh(self):
        if self.stack:
            self.wakeup(self.stack.pop())

    # Additional Handle

    def restore(self):
        u'''
        Handle for come back. Implemented by subclass.
        '''
        raise NotImplementedError, u"How to resotre at `%s` ?" % self.__mark__

    def message(self, msg):
        raise NotImplementedError, u"How to show message in `%s` ?" % self.__mark__

    def notify(self, msg):
        raise NotImplementedError, u"How to show notify in `%s` ?" % self.__mark__
    
    def get(self,data):
        raise NotImplementedError, u"How to reation in `%s` ?" % self.__mark__

    check_perm = NotImplementedError
    
    def is_finish(self,data):
        return data in ac.ks_finish

    def render_str(self, filename, **kwargs):
        t = self._jinja_env.get_template(filename)
        s = t.render(session=self.session,
                     user=self.session.user,
                     uwidth=self.format_width,
                     **kwargs)
        return s

    def do_command(self, command):
        if command :
            getattr(self, command)()

    def readline(self,acceptable=ac.is_safe_char,finish=ac.ks_finish,buf_size=20, prompt=u'', prefix=u''):
        '''
        Return the string when `finish` key recv, return False while recv a k_ctrl_c
        '''
        if prompt :
            self.write(prompt)
        if prefix :
            buf = list(prefix)
            self.write(prefix)
        else:
            buf = []
        while True:
            char = self.read_secret()
            if char in ac.ks_delete :
                if buf :
                    data = buf.pop()
                    self.write(ac.backspace * ac.srcwidth(data))
                    continue
            elif char in finish :
                return u''.join(buf)
            elif char == ac.k_ctrl_c:
                return False
            elif acceptable(char):
                if len(buf) < buf_size:
                    buf.append(char)
                    self.write(char)
        return u''.join(buf)

    readline_safe = readline
    
    def select(self,msg,options,finish=ac.ks_finish):
        if options :
            s = 0
            l = len(options) -1
            while True:
                msg(options[s])
                d = self.read_secret()
                if d == ac.k_up :
                    if s :
                        s -= 1
                elif d == ac.k_down:
                    if s<l :
                        s += 1
                elif d in u'123456789':
                    s = min(l,int(d)-1)
                elif d in finish :
                    return s
                elif d == ac.k_ctrl_c:
                    return False
        return False

    def goto_history(self):
        self.suspend('history')

    # def top_bar(self):
    #     self.render('top')

    # def bottom_bar(self):
    #     self.render('bottom')

        # self.render('bottom_msg',messages=msg)
        # self.pause()
        # self.render('bottom')
        # self.table.refresh_cursor()

class BaseSelectFrame(BaseAuthedFrame):

    menu_start_line = None  ### Should be num in subclass.

    def load_all(self):
        '''
        return (menu, height, background)
        where menu :: (real, pos, shortcuts, text)
        it may be useful Colmenu.tiday to tida such a list:
           [  (desc, real, shortcuts, [pos]) ... ]
        '''
        raise NotImplementedError

    PLACE = u'菜单'

    def bottom_bar(self):
        self.render('bottom')

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render('top_msg', message=msg)
        self.menu.refresh_cursor_gently()

    def message(self, msg):
        self.write(ac.move2(24, 1))
        self.render('bottom_msg', message=msg)
        self.menu.refresh_cursor_gently()

    def initialize(self):
        super(BaseSelectFrame, self).initialize()
        self.menu = self.load(ColMenu)
        menu, height, background = self.load_all()
        self.menu.setup(menu,
                        height,
                        ''.join((ac.move2(self.menu_start_line, 1) ,
                                 background)))
        self.restore()

    def restore(self):
        self.cls()
        self.top_bar()
        self.bottom_bar()
        self.menu.restore()

    def get(self,data):
        # has_new_mail = manager.notify.check_mail_notify(self.userid)
        # if has_new_mail :
        #     self.session.notify = 
        #     self.notify(u'您有 %s 封未邮件！' % has_new_mail)
        if data in ac.ks_finish:
            self.finish()
        self.menu.send_shortcuts(data.lower())
        self.menu.do_command(config.hotkeys['menu_menu'].get(data))
        self.do_command(config.hotkeys['menu'].get(data))
        self.do_command(config.hotkeys['g'].get(data))

    def right_or_finish(self):
        if not self.menu.move_right():
            self.finish()

    def left_or_finish(self):
        if not self.menu.move_left():
            self.goto_back()

    def finish(self):
        raise NotImplementedError
    
class BaseMenuFrame(BaseSelectFrame):

    menu_start_line = 11
    anim_start_line = 3

    def load_all(self):
        '''
        return (menu, height, background)
        where menu :: (real, pos, shortcuts, text)
        it may be useful Colmenu.tiday to tida such a list:
           [  (desc, real, shortcuts, [pos]) ... ]
        '''
        raise NotImplementedError

    def initialize(self):
        anim_data = self.get_anim_data()
        self.anim = self.load(Animation, anim_data,
                              start_line=self.anim_start_line)
        super(BaseMenuFrame, self).initialize()

    def restore(self):
        self.cls()
        self.top_bar()
        self.bottom_bar()
        self.anim.launch()
        self.menu.restore()

    def get_anim_data(self):
        return tidy_anim(self.render_str('active'), 7)

    def finish(self):
        args = self.menu.fetch()
        if isinstance(args,str):
            self.suspend(args)
        else:
            self.suspend(args[0],**args[1])
    
class BaseTableFrame(BaseAuthedFrame):

    ### Handler

    def quick_help(self):
        raise NotImplementedError
    
    def print_thead(self):
        raise NotImplementedError

    def notify(self, msg):
        raise NotImplementedError

    def get_default_index(self):
        raise NotImplementedError

    def get_data(self, start, limit):
        raise NotImplementedError

    def wrapper_li(self, li):
        raise NotImplementedError
    
    def get_total(self):
        raise NotImplementedError

    def catch_nodata(self, e):
        raise NotImplementedError(u'What to do while cannot catch anything [%s] ' % e.message)

    def load_table(self):
        try:
            return self.load(FinitePagedTable, self.get_data, self.wrapper_li,
                             get_last=self.get_total,
                             start_num=self.get_default_index(),
                             start_line=4, height=20)
        except NullValueError as e:
            self.catch_nodata(e)
            self.goto_back()
                           
    def initialize(self):
        super(BaseTableFrame, self).initialize()
        self.table = self.load_table()
        self.init_screen()

    def bottom_bar(self):
        self.render(u'bottom')

    def message(self, msg):
        self.session.message = msg
        self.write(ac.move2(24, 1))
        self.render(u'bottom_msg', message=msg)
        self.table.restore_cursor_gently()
        
    def init_screen(self):
        self.cls()
        self.top_bar()
        self.push('\r\n')
        self.quick_help()
        self.print_thead()
        self.bottom_bar()
        self.table.restore_screen()

    def restore(self):
        try:
            # self.table.reload()        ###############   Ugly!!!
            self.table.goto(self.get_default_index())
        except TableLoadNoDataError:
            self.goto_back()
        else:
            self.init_screen()

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['table_table'].get(data))
        self.do_command(config.hotkeys['table'].get(data))

    def read_lbd(self, reader):
        u'''
        Wrapper real read function.
        '''
        self.write(u''.join((ac.move2(24,1),  ac.kill_line)))
        res = reader()
        self.write(u'\r')
        self.bottom_bar()
        self.table.restore_cursor_gently()
        return res

    def readline(self, acceptable=ac.is_safe_char, finish=ac.ks_finish,\
                     buf_size=20, prompt=u'', prefix=u''):
        return self.read_lbd(lambda : super(BaseTableFrame, self).\
                                 readline(acceptable, finish, 
                                          buf_size, prompt, prefix=prefix))

    def readnum(self, prompt=u''):
        no = self.readline(acceptable=lambda x:x.isdigit(),
                           buf_size=8,  prompt=prompt)
        if no :
            return int(no) - 1
        else :
            return False

    def read_with_hook(self, hook, buf_size=20, prompt=u''):
        self.write(u''.join((ac.move2(2,1),
                            ac.kill_line)))
        if prompt:
            self.write(prompt)
        buf = []
        while len(buf) < buf_size:
            ds = self.read_secret()
            ds = ds or ds[0]
            if ds == ac.k_backspace:
                if buf:
                    data = buf.pop()
                    self.write(ac.backspace)
                continue
            elif ds in ac.ks_finish:
                break
            elif ds == ac.k_ctrl_c:
                buf = False
                break
            else:
                if ds.isalnum() :
                    buf.append(ds)
                    self.write(ds)
                    hook(u''.join(buf))
        self.write(u'\r')
        self.quick_help()
        self.table.restore_cursor_gently()
        if buf is False :
            return buf
        else:
            return u''.join(buf)                

class BaseBoardListFrame(BaseTableFrame):

    boards = []

    # def top_bar(self):
    #     self.render('top')
    #     self.writeln()
        
    def quick_help(self):
        self.writeln(config.str[u'BOARDLIST_QUICK_HELP'])

    def print_thead(self):
        self.writeln(config.str[u'BOARDLIST_THEAD'])

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render(u'top_msg', messages=msg)
        self.table.restore_cursor_gently()

    def get_default_index(self):
        raise NotImplementedError

    def get_data(self, start, limit):
        raise NotImplementedError
    
    def wrapper_li(self, li):
        return self.render_str(u'boardlist-li', **li)

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['g_table'].get(data))
        self.table.do_command(config.hotkeys['boardlist_table'].get(data))
        self.do_command(config.hotkeys['boardlist'].get(data))
        if data in config.hotkeys['boardlist_jump']:
            self.suspend(config.hotkeys['boardlist_jump'][data])
            
    def finish(self):
        self.suspend(u'board', board=self.table.fetch())
    
    def catch_nodata(self, e):
        self.cls()
        self.writeln(u'没有讨论区！')
        self.pause()
        self.goto_back()

    ######################

    def goto_last(self):
        self.table.goto(self.board_total-1)

    def goto_line(self):
        no = self.readnum()
        if no is not False:
            self.table.goto(no)
        else:
            self.table.refresh_cursor_gently()
            self.message(u'放弃输入')

    def goto_with_prefix(self,prefix):  # // Ugly but work.
        data = self.boards
        prefix = prefix.lower()
        for index,item in enumerate(data):
            if item[u'boardname'].lower().startswith(prefix):
                self.write(ac.save)
                self.table.restore_cursor_gently()
                self.table.goto(index)
                self.write(ac.restore)
                return
            
    def search(self):
        self.read_with_hook(hook = lambda x : self.goto_with_prefix(x) ,
                            prompt=u'搜寻讨论区：')
        self.table.restore_cursor_gently()

    def sort(self, mode):
        if mode == 1 :
            self.boards.sort(key = lambda x: \
                                 manager.status.board_online(x[u'boardname'] \
                                                                 or 0),
                            reverse=True)
        elif mode == 2:
            self.boards.sort(key = lambda x: x[u'boardname'])
        elif mode == 3:
            self.boards.sort(key = lambda x: x[u'description'])
        else:
            self.boards.sort(key = lambda x:x[u'bid'])
        self.table.goto(self.table.fetch_num())

    def change_sort(self):
        self.sort_mode += 1
        if self.sort_mode > 3 :
            self.sort_mode = 0
        self.sort(self.sort_mode)
        self.restore()
        self.message(config.str[u'MSG_BOARDLIST_MODE_%s'%self.sort_mode])

    def watch_board(self):
        self.suspend(u'query_board', board=self.table.fetch())

    def add_to_fav(self):
        manager.favourite.add(self.userid, self.table.fetch()[u'bid'])
        self.message(u'预定版块成功！')

    def remove_fav(self):
        manager.favourite.remove(self.userid, self.table.fetch()[u'bid'])
        self.message(u'取消预定版块成功！')

    def show_help(self):
        self.suspend('help', page='boardlist')

class Editor(TextEditor, TextEditorAreaMixIn):

    fground_string = {
        u'0':(u'[#30%]', u'[%#]'),
        u'1':(u'[#31%]', u'[%#]'),
        u'2':(u'[#32%]', u'[%#]'),
        u'3':(u'[#33%]', u'[%#]'),
        u'4':(u'[#34%]', u'[%#]'),
        u'5':(u'[#35%]', u'[%#]'),
        u'6':(u'[#36%]', u'[%#]'),
        u'7':(u'[#37%]', u'[%#]'),
        }

    bground_string = {
        u'0':(u'[#40%]', u'[%#]'),
        u'1':(u'[#41%]', u'[%#]'),
        u'2':(u'[#42%]', u'[%#]'),
        u'3':(u'[#43%]', u'[%#]'),
        u'4':(u'[#44%]', u'[%#]'),
        u'5':(u'[#45%]', u'[%#]'),
        u'6':(u'[#46%]', u'[%#]'),
        u'7':(u'[#47%]', u'[%#]'),
        }

    special_style = {
        u'i':(u'[#3%]', u'[%#]'),
        u'u':(u'[#4%]', u'[%#]'),
        u'b':(u'[#1%]', u'[%#]'),
        u'l':(u'[#5%]', u'[%#]'),
        u'n':(u'[#7%]', u'[%#]'),
        }

    def _insert_style(self):
        self.hint(u'b) 背景色 f)字体色 r)样式复原')
        char = self.frame.read_secret()
        if char == 'b' :
            self.hint(u'背景颜色? 0)黑 1)红 2)绿 3)黄 4)深蓝 5)粉红 6)浅蓝 7)白')
            char2 = self.frame.read_secret()
            if char2 in self.bground_string :
                return self.bground_string[char2]
        elif char == 'f' :
            self.hint(u'字体颜色? 0)黑 1)红 2)绿 3)黄 4)深蓝 5)粉红 6)浅蓝 7)白')
            char2 = self.frame.read_secret()
            if char2 in self.fground_string :
                return self.fground_string[char2]
        elif char == 'e' :
            self.hint(u'特殊样式? i)斜体 u)下划线 b)加粗 l)闪烁 n)反转')
            char2 = self.frame.read_secret()
            if char2 in self.special_style:
                return self.special_style[char2]
        elif char == 'r' :
            return (u'[#%]', u'')
        elif char == ac.esc :
            return self.esc

    def insert_style(self):
        res = self._insert_style()
        if isinstance(res, tuple) :
            self.insert_string(*res)
        elif res is not None :
            self.force_insert_char(res)

    def insert_style_area(self):
        res = self._insert_style()
        if isinstance(res, tuple) :
            self.insert_string_area(*res)
                
    def bottom_bar(self,msg=u''):
        self.frame.push(ac.move2(24,0))
        self.frame.render(u'bottom_edit', message=msg, l=self._hover_col, r=self._hover_row)
        self.fix_cursor()

    def do_command(self, cmd):
        getattr(self, cmd)()
        self.bottom_bar()

    def fetch_all(self):
        text = super(Editor, self).fetch_all()
        return text.replace(self.esc, ac.esc)

    def fetch_lines(self):
        text = self.fetch_all()
        return text.split('\r\n')

class BaseEditFrame(BaseAuthedFrame):

    def fetch_all(self):
        text = self.e.fetch_all()
        text = telnet2style(text)
        return text        

    def fetch_lines(self):
        return self.fetch_all().split('\r\n')

    def finish(self):
        raise NotImplementedError

    def restore(self):
        self.e.restore_screen()

    restore_screen = restore

    def notify(self, msg):
        pass ############           Not ImplamentedError

    def message(self,content):
        self.e.bottom_bar(content[:40])
        
    def get(self,char):
        if char in config.hotkeys['edit_editor'] :
            self.e.do_command(config.hotkeys['edit_editor'][char])
        elif char in config.hotkeys['edit']:
            getattr(self, config.hotkeys['edit'][char])()
        elif char == config.hotkeys['edit_2ndcmd_start'] :
            char2 = self.read_secret()
            if char2 in config.hotkeys['edit_2nd'] :
                getattr(self.e, config.hotkeys['edit_2nd'][char2])()
        else:
            self.e.insert_char(char)

    # def copy_to_superclip(self):
    #     text = self.e.remove_area()
    #     manager.clipboard.append_clipboard(self.userid, value=text)

    # def insert_superclip(self):
    #     clipboard = self.u(manager.clipboard.get_clipboard(self.userid))
    #     self.e.insert_paragraph(clipboard)
    #     self.restore()
        
    def quit_iter(self):
        self.message(u'放弃本次编辑操作？')
        d = self.readline()
        if not d :
            self.goto_back()

    def show_help(self):
        self.suspend(u'help',page='edit')

    def initialize(self, spoint=0, text=u''):
        assert isinstance(text, unicode) or (isinstance(text, list) and\
                                                 all( isinstance(x, list) for x in text) and\
                                                 all( all(isinstance(char, unicode) for char in line)
                                                      for line in text))
        self.e = self.load(Editor, text, spoint)
        self.restore_screen()

class TextBox(SimpleTextBox):

    def message(self, message):
        self.frame.write(ac.move2(24,1))
        self.frame.render(u'bottom_view', message=message, s=self.s, maxs=self.h)

    def fix_bottom(self):
        self.message(u'')

class BaseTextBoxFrame(BaseAuthedFrame):

    hotkeys = {}

    u'''
    Inherit this class and rewirte the `get_text` method
    to display the text.
    It's useful to copy the `key_maps` and `textbox_cmd`
    and add new key/value into them.
    '''

    def get_text(self):
        raise NotImplementedError

    def restore(self):
        self.textbox.restore_screen()
        self.textbox.fix_bottom()

    def reset_text(self, text):
        self.textbox.set_text(self.get_text())
        self.restore()

    def message(self,msg):
        self.textbox.message(msg)

    def notify(self, msg):
        self.textbox.message(msg)  #########
        
    def get(self,data):
        if data in ac.ks_finish:
            self.finish(True)
        self.textbox.do_command(config.hotkeys['view_textbox'].get(data))
        self.do_command(config.hotkeys['view'].get(data))
        self.do_command(self.hotkeys.get(data))
        
    def initialize(self):
        super(BaseTextBoxFrame, self).initialize()
        self.textbox = self.load(TextBox, self.get_text(), self.finish)
        self.restore()

    def _go_link(self,line):
        s = line.split()
        if (len(s) > 0) and (s[0] in self.jump_marks) :
            m = s[0]
            status = mark[m].try_jump(self, s)
            if status :
                self.suspend(m,**status)
                
    def go_link(self):
        self.write(ac.move2(24,1) + ac.kill_line)
        d = self.readline()
        self._go_link(d)
        self.table.fix_bottom()

    links_re = re.compile(r'\[[^\]]*\]\(/(p)/(.+)/(\d+)\)|'
                          r'\[[^\]]*\]\(/(h)/(.+)\)')

    jump_marks = {
        u'p':u'post',
        u'h':u'help',
        }

    def hint_link(self,t):
        if t[0] == u'p' :
            self.links_args = t[0],t[1:3]
            return u'去看 %s 区的 %s 号文？' % (t[1],t[2])
        elif t[3] == u'h' :
            self.links_args = t[3],t[4:5]
            return u'去看 %s 的帮助页面？' % (t[4])
        return u'错误的跳转标记'

    def check_jump(self):
        n = self.jump_marks[self.links_args[0]]
        r = mark[n].try_jump(self, self.links_args[1])
        if r :
            self.suspend(n,**r)
        else:
            self.message(u'不是一个有效的跳转标志')
            return

    def find_options(self, opstring):
        for row in range(0, self.limit):
            col = self.lines.find( opstring )
            if col != - 1:
                return row,col
        return None

    def re2str(self, reop):
        return

    def select_and_jump(self,text):
        options = re.findall(self.links_re,text)
        if not options :
            self.message(u'没有可用的跳转标志')
            return
        self.select_start = 0
        res = self.select(lambda x :
                              self.message(self.hint_link(x)),
                          options)
        if res is False :
            self.message(u'放弃跳转')
        else:
            self.check_jump()

    def jump_from_screen(self):
        text,self.lines = self.textbox.getscreen_with_raw()
        self.select_and_jump(text)

    def show_help(self):
        self.suspend('help', page='view')

def chunks(data, height):
    for i in xrange(0, len(data), height+1):
        yield (u'\r\n'.join(data[i:i+height]),int(data[height]))

def list_split(data, height):
    for i in xrange(0, len(data), height):
        yield data[i:i+height]

def tidy_anim(text, height):
    l = text.split(u'\r\n')
    return list(chunks(l, height))

def gen_quote(post):
    max_quote_line = 5
    owner = manager.userinfo.get_user(post['owner'])
    return ''.join([
            u'\n【 在 %s ( %s ) 的大作中提到: 】\n:' % (owner['userid'],
                                                   owner['nickname']),
            '\n:'.join(post['content'].split('\n')[:max_quote_line]),
            ])

def gen_quote_mail(mail):
    max_quote_line = 5
    owner = manager.userinfo.get_user(mail['fromuserid'])
    return ''.join([
            u'\n【 在 %s ( %s ) 的来信中提到: 】\n:' % (owner['userid'],
                                                        owner['nickname']),
            '\n:'.join(mail['content'].split('\n')[:max_quote_line])
            ])

def wrapper_index(data, start):
    for index in range(len(data)):
        data[index]['index'] = index + start
    return data

inv_re = re.compile(r'@(\w{3,20}) ')
def find_all_invert(content):
    return inv_re.findall(content)
