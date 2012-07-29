#!/usr/bin/python2
# -*- coding: utf-8 -*-

from datetime import datetime
import functools
import re

from chaofeng import Frame
import chaofeng.ascii as ac
from chaofeng.ui import TextEditor, LongTextBox, PagedTable, Animation, ColMenu,\
    NullValueError
import config
from template import env
from model import manager

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
        s = self.s(source)
        return self.u('%*s' % (width, s))

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
        while len(buf) < buf_size:
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
                elif d.isalnum():
                    buf.append(d)
                    self.write(d)
        return u''.join(buf)                        

    def render(self, filename, **kwargs):
        self.write(self.render_str(filename, **kwargs))

class BaseAuthedFrame(BaseFrame):

    def get_pipe(self):
        return self.session[u'_$$pipe$$']

    def set_pipe(self, value):
        self.session[u'_$$pipe$$'] = value

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
        self.session.history.append(self)
        self.goto(where,**kwargs)

    def goto_back(self):
        u'''
        Go back to previous frame save in
        history.
        '''
        self.session.history.append(self)
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
        raise NotImplementedError, u"How to reation in `%` ?" % self.__mark__
    
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
        raise NotImplementedError

    def top_bar(self):
        self.render('top')

    def bottom_bar(self):
        self.render('bottom')

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render('top_msg', messages=msg)
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
        if data in ac.ks_finish:
            self.finish()
        self.menu.send_shortcuts(data)
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

    def top_bar(self):
        raise NotImplementedError

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

    def catch_nodata(self, e):
        raise NotImplementedError(u'What to do while cannot catch anything [%s] ' % e.message)

    def load_table(self):
        try:
            return self.load(PagedTable, self.get_data, self.wrapper_li,
                             self.get_default_index(),
                             start_line=4, page_limit=20)
        except NullValueError as e:
            self.catch_nodata(e)
            self.goto_back()
                           
    def initialize(self):
        super(BaseTableFrame, self).initialize()
        self.table = self.load_table()
        self.restore()

    def bottom_bar(self):
        self.render(u'bottom')

    def message(self, msg):
        self.session.message = msg
        self.write(ac.move2(24, 1))
        self.render(u'bottom_msg', message=msg)
        self.table.restore_cursor_gently()

    def restore(self):
        self.cls()
        self.top_bar()
        self.quick_help()
        self.print_thead()
        self.bottom_bar()
        self.table.reload()        ###############   Ugly!!!
        self.table.restore_screen()

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['table_table'].get(data))
        self.do_command(config.hotkeys['table'].get(data))

    def read_lbd(self, reader):
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
        if no is not False :
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
            ds = self.read_secret(2)
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

    def top_bar(self):
        self.render(u'top')
        self.writeln()
        
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

    def finish(self):
        self.suspend(u'board', board=self.table.fetch())

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
        for index,item in enumerate(data):
            if item[u'boardname'].startswith(prefix):
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
                                manager.online.board_online(x[u'boardname'] or 0),
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

class BaseFormFrame(BaseTableFrame):

    def get_data_index(self, index):
        u'''
        tuple like ( attrname, attrstring ) is return.
        '''
        raise NotImplementedError

    def handle(self, index):
        raise NotImplementedError

    def submit(self):
        raise NotImplementedError

    def get_data_len(self):
        raise NotImplementedError

    def get_default_values(self):
        raise NotImplementedError

    def top_bar(self):
        self.render(u'top')
        self.writeln()

    def quick_help(self):
        self.writeln(config.str[u'FORM_QUICK_HELP'])

    def print_thead(self):
        self.writeln(config.str[u'FORM_THEAD'])

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render(u'top_msg', messages=msg)
        self.table.restore_cursor_gently()

    def get_default_index(self):
        return 0

    def get_data(self, start, limit):
        return map(self.get_data_index, range(start, min(self.get_data_len(), start+limit)))

    def wrapper_li(self, li):
        return u'  %s%-1s' % (self.format_width(li[0], -30), li[1])

    def finish(self):
        self.handle(self.table.fetch_num())

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['g_table'].get(data))
        self.do_command(config.hotkeys['table'].get(data))
        self.do_command(config.hotkeys['form'].get(data))

    def initialize(self):
        self.form = self.get_default_values()
        super(BaseFormFrame, self).initialize()

class Editor(TextEditor):

    def bottom_bar(self,msg=u''):
        self.write(ac.move2(24,0))
        self.frame.render(u'bottom_edit', message=msg, l=self.l, r=self.r)
        self.fix_cursor()

class BaseEditFrame(BaseAuthedFrame):

    def finish(self):
        raise NotImplementedError

    def restore_screen(self):
        self.e.do_editor_command(u"refresh")

    def notify(self, msg):
        pass ############           Not ImplamentedError

    def restore(self):
        self.e.do_editor_command(u"refresh")

    def message(self,content):
        self.e.bottom_bar(content[:40])
        
    def get(self,char):
        # if self.ugly :
            # char = self.ugly + char
            # self.ugly = u''
        # elif len(char) == 1 and ac.is_gbk_zh(char):
            # self.ugly = char
            # return
            
        if char in config.hotkeys['edit_editor'] :
            self.e.do_editor_command( config.hotkeys['edit_editor'][char])
        elif char == config.hotkeys['edit_2ndcmd_start'] :
            x = self.read_secret()
            if x in config.hotkeys['edit_editor_2nd']:
                self.e.do_editor_command(config.hotkeys['edit_editor_2nd'][x])
        elif char in config.hotkeys['edit']:
            getattr(self, config.hotkeys['edit'][char])()
        else:
            self.e.safe_insert_iter(char)

    def copy_to_superclip(self):
        text = self.e.get_clipboard()
        manager.clipboard.append_clipboard(self.userid, value=text)

    def insert_superclip(self):
        clipboard = self.u(manager.clipboard.get_clipboard(self.userid))
        self.e.insert_paragraph(clipboard)
        self.restore()
        
    def quit_iter(self):
        self.message(u'放弃本次编辑操作？')
        d = self.readline()
        if not d :
            self.goto_back()

    def show_help(self):
        self.suspend(u'help',page='edit')

    def initialize(self, spoint=0, text=u''):
        assert isinstance(text, unicode)
        self.e = self.load(Editor, height=23, hislen=5, dis=10)
        self.e.set_text(text, spoint)
        self.ugly = u'' # 修复单字节发送的bug （sterm）
        self.restore_screen()

    def read_title(self, prompt=u'', prefix=u''):
        return self.readline(prompt=prompt, prefix=prefix, buf_size=40)

class TextBox(LongTextBox):

    def message(self, message):
        self.write(ac.move2(24,1))
        self.frame.render(u'bottom_view', message=message, s=self.s, maxs=self.max)

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
        self.textbox.refresh_all()
        self.textbox.fix_bottom()

    def reset_text(self, text):
        self.textbox.set_text(text)
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

    def set_text(self,text):
        self.textbox.set_text(text)
        self.textbox.refresh_all()
        self.textbox.fix_bottom()

    def _go_link(self,line):
        s = line.split()
        if (len(s) > 0) and (s[0] in self.jump_marks) :
            m = s[0]
            status = mark[m].try_jump(s)
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
        r = mark[n].try_jump(self.links_args[1])
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

def chunks(data, height):
    for i in xrange(0, len(data), height+1):
        yield (u'\r\n'.join(data[i:i+height]),int(data[height]))

def tidy_anim(text, height):
    l = text.split(u'\r\n')
    return list(chunks(l, height))
