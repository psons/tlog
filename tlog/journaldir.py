#!/usr/local/bin/python3 -d
import sys

# journaldir.py
from typing import TextIO

from git import Repo
from git import IndexFile

"""
determine directory for journal files based on current year and month.
if invoked as script, print it to stdout so a shell alias can cd there.

Composition: Contains all the file system operations needed by tlog.py
"""
import datetime
import os
import re
from os import listdir
from os.path import isfile, join


class TaskSourceException(Exception):
    'Task source exception indicates a failure in a data source for endeavors, stories,  etc '

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


default_path = os.path.expanduser('~') + '/journal'

convention_journal_root = os.getenv('JOURNAL_PATH', default_path)
endeavor_dir = convention_journal_root + "/Endeavors"
journal_pat = re.compile(
    '[Jj]ournal-[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].md')
story_pat = re.compile('.*story.md')


class UserPaths:
    """
    Builds the useful data paths based on the documented structure:
        journal_dir:
        << various year subdirectories >>
                << various month subdirectories >>
        << possibly the endeavor_dir location>>
    endeavor_dir:
            endeavors.md
            << various endeavor subdirectories >>
                << various *story.txt files containing task items >>
    """
    def __init__(self, user_journal_path=convention_journal_root, user_endeavor_dir=endeavor_dir):
        if os.path.isdir(user_journal_path):
            self.journal_path = user_journal_path
        else:
            raise TaskSourceException(user_journal_path + " for journals is not a directory")
        self.endeavor_path = user_endeavor_dir
        # its ok if dir and file don't exist. j read_file_str() will just return ""
        self.endeavor_file = os.path.join(self.endeavor_path, "endeavors.md")
        default_endeavor_dir = os.path.join(self.endeavor_path, "default")
        self.new_task_story_file = os.path.join(default_endeavor_dir, "new task story.md")
        self.git_repo_obj = None

    def git_init_journal(self):
        print(self.journal_path)
        self.git_repo_obj = make_git_repo(self.journal_path)

    def git_add_all(self):
        untracked = self.git_repo_obj.untracked_files
        commit_message = ",".join(untracked)[0:50]
        commit_message = "tlog commit"
        journal_index: IndexFile = self.git_repo_obj.index
        self.git_repo_obj.git.add('--all')
        journal_index.commit(commit_message)

    def __str__(self):
        return "\n".join(["JournalPath: " + self.journal_path,
                          "EndeavorFilePath: " + self.endeavor_file])


def get_file_names_by_pattern(dir_name, a_pattern):
    """
	Get the file names in a directory that match a compiled regex 
	pattern that are not themselves directories.
	"""
    matching_file_list = []
    if not os.path.isdir(dir_name):
        return matching_file_list

    for f in sorted(listdir(dir_name)):
        fqp = join(dir_name, f)
        if isfile(fqp) and a_pattern.match(f):
            matching_file_list.append(fqp)
    return matching_file_list


class Daily:
    def __init__(self, dt: datetime.datetime = None):
        """
        Set some daily values needed in some names and labels
        :param dt: type: datetime.datetime
        """
        self.jroot = convention_journal_root
        self.dt = dt or datetime.datetime.now()
        # see http://strftime.org/
        yyyy = self.dt.strftime('%Y')
        mm = self.dt.strftime('%m')
        dow = self.dt.strftime('%a')
        dd = self.dt.strftime('%d')
        dom = self.dt.strftime('%-d')
        dayth_dict = {'1': "st", '2': "nd", '3': "rd", '4': "th",
                      '5': "th", '6': "th", '7': "th", '8': "th", '9': "th", '10': "th",
                      '11': "th", '12': "th", '13': "th", '14': "th", '15': "th", '16': "th",
                      '17': "th", '18': "th", '19': "th", '20': "th", '21': "expected_story_text", '22': "nd",
                      '23': "rd", '24': "th", '25': "th", '26': "th", '27': "th", '28': "th",
                      '29': "th", '30': "th", '31': "expected_story_text"}

        self.domth = dow + ' ' + dom + dayth_dict[dom]
        self.jdir = os.path.join(self.jroot, yyyy, mm)
        self.debug_log_file = os.path.join(self.jroot, "tl.debug.log")
        # self.user_log_file = os.path.join(self.jroot, "tl.user.log")
        self.info_log_file = os.path.join(self.jroot, "tl.info.log")
        self.cday_journal_fname = 'journal' + '-' + yyyy + '-' + mm + '-' + dd + '.md'
        self.cday_todo_fname = 'journal' + '-' + yyyy + '-' + mm + '-' + dd + '.md'
        self.cday_resolved_fname = 'resolved' + '-' + yyyy + '-' + mm + '-' + dd + '.md'

    def __str__(self):
        return f"{self.jdir} {self.cday_journal_fname} {self.domth}"


def load_endeavor_stories(user_path_obj):
    """return a list of StoryDir objects for each entry in the endeavors file."""
    # More advanced versions of endeavor file format later.
    endeavor_text = read_file_str(user_path_obj.endeavor_file)
    # print("endeavor_text:", endeavor_text)
    return [StoryDir(os.path.join(user_path_obj.endeavor_path, e_str))
            for e_str in endeavor_text.split()]


def load_endeavors_deprecated(user_path_obj):
    endeavor_text = read_file_str(user_path_obj.endeavor_file)
    print("endeavor_text:", endeavor_text)
    return [Endeavor_deprecated(e_str, user_path_obj) for e_str in endeavor_text.split()]

def path_join(p, f):
    "wrapper helps prevent module os from being needed in calling modules."
    return os.path.join(p, f)


def read_file_str(filepath) -> str:
    data = ""
    if os.path.isfile(filepath):
        with open(filepath, 'r') as data_file:
            data = data_file.read()
    return str(data)

def write_filepath(new_content, filepath):
    # todo crashing: make sure the directories and file exist.
    base_dir: str = os.path.dirname(filepath)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    sfd: TextIO
    with open(filepath, "w") as sfd:
        sfd.write(new_content)

def write_dir_file(new_content, dir_name, doc_name):
    filepath = os.path.join(dir_name, doc_name)
    if os.path.isfile(filepath):
        previous_content = read_file_str(filepath)
        if previous_content == new_content:
            print("new content same as old. Nothing written.")
        else:
            print("new content is different than content from old file. renaming")
            # if writing, do this:
            olddir = os.path.join(dir_name, "old")
            if not os.path.isdir(olddir):
                os.makedirs(olddir)
            os.rename(filepath, os.path.join(olddir, doc_name))
            jfd = open(filepath, "w")
            jfd.write(new_content)
            jfd.close
    else:
        jfd = open(filepath, "w")
        jfd.write(new_content)
        jfd.close


def make_git_repo(path):
    new_rw_repo = Repo.init(path)
    # new_rw_repo.config_reader()  # get a config reader for read-only access
    with new_rw_repo.config_writer():  # get a config writer to change configuration
        pass  # call release() to be sure changes are written and locks are released
    # print(new_rw_repo)
    return new_rw_repo


def init(aDir):
    """
	create new journal dir
	:param aDir: a directory to be created if it does not exist.
	"""
    if not os.path.exists(aDir):
        os.makedirs(aDir)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "init":
        init(journal_dir)

    print(journal_dir)


# print(dom + dayth_dict[dom])

def get_prior_dir(search_dir):
    """search_dir ends with a path like somthing/yyyy/mm
	then the pathname of the prior dir  will be returned"""
    if search_dir == "/":
        return None
    if search_dir[-1] == '/':
        search_dir = search_dir[0:-1]  # get rid of trailing '/' before split
    year_path, month_part = os.path.split(search_dir)
    base_path, year_part = os.path.split(year_path)
    prior_months = {"01": "12", "02": "01", "03": "02", "04": "03",
                    "05": "04", "06": "05", "07": "06", "08": "07",
                    "09": "08", "10": "09", "11": "10", "12": "11"}
    try:
        year_int = int(year_part)
    except ValueError:
        return None  # bad year

    if month_part not in prior_months.keys():
        return None  # bad month

    mm = prior_months[month_part]
    if mm == "12":
        year_int -= 1

    if year_int <= 0:
        return None  # underflow year

    year_str = '{:04d}'.format(year_int)
    return os.path.join(base_path, year_str, mm)


class Endeavor_deprecated:
    def __init__(self, name, a_user_path_obj):
        self.name = name
        self.dir_path = os.path.join(a_user_path_obj.endeavor_path, self.name)
        self.story_list = get_file_names_by_pattern(self.dir_path, story_pat)

    def __str__(self):
        return "Endeavor name:{} stories:{}".format(self.name, str(self.story_list))


class StoryDir:
    """
    loads a list of story files with full path info
    """
    def __init__(self, sdir):
        """
        Given a directory path, loads list of stories
        :param sdir: directory path
        """
        self.path = sdir
        if os.path.isdir(sdir):
            self.story_list = get_file_names_by_pattern(sdir, story_pat)
        else:
            raise TaskSourceException("{} is not a directory, so can not be a StoryDir".format(sdir))

    def __str__(self):
        return "StoryDir:({}):".format(self.path) + ",".join(self.story_list)
