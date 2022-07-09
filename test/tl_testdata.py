#tl_testdata.py
import os

import journaldir
import unit_test_tmp_dir
from tlconst import apCfg
"""
Test data with tlog semantic tasks leaders, section headers and attribute syntax.
"""

ad1 = "aDocAttribute"
vd1 = " TheDocValue"
vd2 = " TheChangedDocValue"
doc_attrib_line = ad1 + ':' + vd1
header_line = "# The Header"
as1 = "aSectionAttribute"
vs1 = " TheSectionValue"
as2 = "aNewSectionAttribute"
vs2 = " TheNewSectionValue"
section_attrib_line = as1 + ':' + vs1
xtask_line = "x - completed task"
xtask_sub_line = " - sub of completed task"
second_header_line = "## a second section"
inprog_task_line = " - sub of in progress task"
ai1 = "anItemAttribute"
vi1 = " TheItemValue"
item_attrib_line1 = ai1 + ':' + vi1
ai2 = "anotherItemAttribute"
vi2 = " AnotherItemValue"
item_attrib_line2 = ai2 + ':' + vi2

default_tlog_home = os.path.expanduser('~')

tlog_home = os.getenv('TLOG_HOME' , default_tlog_home )
data_dir = tlog_home + '/test/data'

dtask_line = "d - do task"
dtask_sub1_line = " - sub item list item 1"
dtask_sub2_line = " - sub item list item 2"
dtask_text_line = "free text"

# this gets computed in a test and is needed as an expected value
# dtask_saved_hash = "titleHash:9b35f4f8b4573f2c8239f0c49463f04f"
dtask_saved_hash = "titleHash:9b35f4f8b4"

dtask_item_text = "\n".join([dtask_line, item_attrib_line1,
                             dtask_sub1_line, dtask_sub2_line, dtask_text_line])

item_2attr_str = "\n".join([item_attrib_line1, item_attrib_line2])
dtask_item_text_w_saved_hash = "\n".join([dtask_line, item_attrib_line1,
                                          dtask_saved_hash,
                                          dtask_sub1_line, dtask_sub2_line, dtask_text_line])
dtask_line_modified = "d - do task changed"
dtask_item_text_w_saved_hash_modified_title = "\n".join([dtask_line_modified,
                                                         item_attrib_line1, dtask_saved_hash,
                                                         dtask_sub1_line, dtask_sub2_line, dtask_text_line])
doc1_text = "\n".join([doc_attrib_line, header_line, section_attrib_line,
                       xtask_line, xtask_sub_line,
                       second_header_line, inprog_task_line,
                       dtask_line, dtask_sub1_line, dtask_sub2_line, dtask_text_line]
                      )
dtask2_line = "d - do another task"
dtask2_sub1_line = " - sub of do another"
sec_two_items = "\n".join([dtask_line, dtask2_sub1_line, dtask2_line, dtask2_sub1_line])
sec_attrib_wrong = "\n".join([header_line, xtask_line, section_attrib_line])
sec_w_attrib = "\n".join([section_attrib_line, header_line])
sec_head = """\
#Section\
"""
sec_item = """\
d - do something\
"""
sec_head_item = """\
#Section
d - do something\
"""
sec_attr_item = """\
DocName:journal-2020-02-22.md
d - do something\
"""
sec_attr1 = """\
DocName:journal-2020-02-22.md\
"""
sec_attr2 = """\
DocName:journal-2020-02-22.md

\
"""
sec_empty = """\


\
"""
is_attrib_section_cases = [
    (sec_head, False),
    (sec_item, False),
    (sec_head_item, False),
    (sec_attr_item, False),
    (sec_attr1, True),
    (sec_attr2, False),
    (sec_empty, False)
]


def getUnitTestUserPathObject():
    """
    gets a UserPath object that is rooted at unit_test_tmp_dir.uttd instead of using the environment
    variables of default locations.
    This is useful to allow 3 separate run environments on a laptop:
     1 - a separate environment were unit tests can set up and tear down.
     2 - a development and user acceptance test environment that uses alternate environment locations
     to quickly mock up and reload test data.
     3 - an actual real tlog environment
    :return:
    """
    ut_journal_root = unit_test_tmp_dir.uttd + apCfg.journal_path_stub
    ut_tmp_root = unit_test_tmp_dir.uttd + apCfg.tmp_path_stub
    ut_endeavor_dir = unit_test_tmp_dir.uttd + apCfg.endeavor_path_stub
    if unit_test_tmp_dir.uttd_exists:
        os.makedirs(ut_journal_root, exist_ok=True)
    else:
        message = f"Create {unit_test_tmp_dir.uttd} to run unit tests that write to files."
        print(message)
        raise NotADirectoryError(message)
    userPathObject = journaldir.UserPaths(ut_journal_root, ut_tmp_root, ut_endeavor_dir)
    return userPathObject
