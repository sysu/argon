
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
