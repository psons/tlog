#testdata.py
import os
default_tlog_home = os.path.expanduser('~')

tlog_home = os.getenv('TLOG_HOME' , default_tlog_home )
data_dir = tlog_home + '/test/data'

dtask_line = "d - do task"