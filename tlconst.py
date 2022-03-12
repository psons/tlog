import os
import re

class apCfg:
    """
    Class to consolidate application literals and environment config.
    """
    # These stub paths are used for test versions of the directories.
    journal_path_stub = '/journal'
    tmp_path_stub = '/tmp/tlog'
    endeavor_path_stub = "/Endeavors"

    default_journal_path = os.path.expanduser('~') + journal_path_stub
    default_tmp_path = os.path.expanduser('~') + tmp_path_stub
    default_endeavor_name = "default"

    convention_log_location = os.getenv('TLOG_TMP', default_tmp_path)
    convention_journal_root = os.getenv('JOURNAL_PATH', default_journal_path)

    endeavor_dir = convention_journal_root + endeavor_path_stub
    journal_pat = re.compile(
        '[Jj]ournal-[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].md')
    story_pat = re.compile('.*story.md')
    priority_pat = re.compile('[pP]rioritized.[mM][Dd]')