'''
use in admin.sh::

import tools.tidy_old_post as o
model.Model.sql_all_boards(o.set_null_sign)
model.Model.sql_all_boards(o.set_new_escape)

'''

set_null_sign = "UPDATE %s SET signature='' "

set_new_escape = "UPDATE %s SET content=REPLACE(content, '\r\n', '\n')"

'''
import tools.tidy_old_post as o
model.Model.sql_all_boards(o.new_look_reply_col)
'''

new_look_reply_col = 'ALTER TABLE %s ADD look_reply boolean NOT NULL default false'

