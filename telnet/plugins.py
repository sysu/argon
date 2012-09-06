@BaseTableFrame.plugin.add_action(ac.k_ctrl_r)
def jump_from_screen(frame):
    options = re.findall(links_re, text)
    if not options:
        frame.message(u'没有可用的跳转标志')
        return
    select_start = 0
    res = frame.select(lambda x:
                           frame.message(hint_link(x)),
                       options)
    if res is False:
        frame.message(u'放弃跳转')
    else:
        n = jump_marks[
