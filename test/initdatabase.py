import sys
sys.path.append('../')

import model
        
def init_database():
    u'''
    初始化数据库。
    '''
    print
    print 'Init Database will kill all data. Are you sure?'
    print
    print 'Type INIT_YES to continue.',
    if raw_input() == 'INIT_YES' :
        print 'Init Database start ...'
        model.init_database()
        print 'Init Database DONE.'
    print 'All DONE.'
