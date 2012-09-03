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
