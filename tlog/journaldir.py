#!/usr/bin/env python -d
#!/usr/local/bin/python3 -d
import sys

# journaldir.py
from typing import TextIO, List

from git import Repo
from git import IndexFile

"""
determine directory for journal files based on current year and month.
if invoked as script, print it to stdout so a shell alias can cd there.

Composition: Contains all the file system operations needed by tlog.py
"""
from tlconst import apCfg
import datetime
import os
import re
from os import listdir
import logging
import tlutil

class UserPaths:
    """
    Verifies that journal_root exists as a directory.
    Builds the useful data paths strings based on the documented structure, but does not create the paths.:
        journal_dir:
        << various year subdirectories >>
                << various month subdirectories >>
        << possibly the endeavor_dir location>>
    endeavor_dir:
            endeavors.md
            << various an_endeavor subdirectories >>
                << various *story.txt files containing task items >>
    """
    def __init__(self, journal_root=apCfg.convention_journal_root,
                 tmp_root=apCfg.convention_log_location, user_endeavor_dir=apCfg.endeavor_dir):
        if os.path.isdir(journal_root):
            self.journal_path = journal_root
        else:
            raise tlutil.TaskSourceException(journal_root + " for journals is not a directory")
        self.endeavor_path = user_endeavor_dir
        # its ok if dir and file don't exist. j read_file_str() will just return ""
        self.endeavor_file = os.path.join(self.endeavor_path, "endeavors.md")
        default_endeavor_dir = os.path.join(self.endeavor_path, apCfg.default_endeavor_name)
        self.new_task_story_file = os.path.join(default_endeavor_dir, "new task story.md")
        self.git_repo_obj = None
        self.tmp_root = tmp_root
        self.old_journal_dir = os.path.join(self.tmp_root, "old")
        self.debug_log_file = os.path.join(self.tmp_root, "tl.debug.log")


    def git_init_journal(self):
        self.git_repo_obj = make_git_repo(self.journal_path)

    def git_add_all(self, daily_o, message):
        untracked = self.git_repo_obj.untracked_files
        # commit_message = ",".join(untracked)[0:50]
        commit_message = f"tlog commit: {message} " + daily_o.j_month_dir
        journal_index: IndexFile = self.git_repo_obj.index
        self.git_repo_obj.git.add('--all')
        journal_index.commit(commit_message)

    def __str__(self):
        return "\n".join(["JournalPath: " + self.journal_path,
                          "EndeavorFilePath: " + self.endeavor_file])


# todo add a test perhaps via a higher level function in tlog
def get_file_names_by_pattern(source_dir_name, a_pattern: re.Pattern) -> List[str]:
    # todo make a default for a_pattern that is a compiled re that matches everything.
    """
	Get the file names in a directory that match a compiled regex 
	pattern that are not themselves directories.
	"""
    matching_file_list: List[str] = []
    if not os.path.isdir(source_dir_name):
        return matching_file_list

    for f in sorted(listdir(source_dir_name)):
        fqp = os.path.join(source_dir_name, f)
        if os.path.isfile(fqp):
                if a_pattern.match(f):
                    matching_file_list.append(fqp)
    return matching_file_list


# todo add a test
def move_files(target_dir_path, file_paths: List[str]):
    """
    move each file in a list to a target directory
    :param target_dir_path:
    :param file_paths:
    :return: None
    """
    if not os.path.isdir(target_dir_path):
        print(f"{target_dir_path} is not a directory")
        raise NotADirectoryError

    for file_path in file_paths:
        dest_file_path = os.path.join(target_dir_path, os.path.basename(file_path))
        os.replace(file_path, dest_file_path)




class Daily:
    def __init__(self, jroot: str, dt: datetime.datetime = None):
        """
        Set some daily values needed in some names and labels
        :param dt: type: datetime.datetime
        """
        self.jroot = jroot
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
        self.j_month_dir = os.path.join(self.jroot, yyyy, mm)  # where j/td files go this month.
        self.jrdir = os.path.join(self.j_month_dir, "resolved")  # subdir for resolved files.
        self.cday_journal_fname = 'journal' + '-' + yyyy + '-' + mm + '-' + dd + '.md'
        self.cday_todo_fname = 'journal' + '-' + yyyy + '-' + mm + '-' + dd + '.md'
        self.cday_resolved_fname = 'resolved' + '-' + yyyy + '-' + mm + '-' + dd + '.md'

    def __str__(self):
        return f"{self.j_month_dir} {self.cday_journal_fname} {self.domth}"


def load_endeavor_stories(user_path_obj):
    """return a list of StoryDir objects for each entry in the endeavors file."""
    # More advanced versions of an_endeavor file format later.
    endeavor_text = apCfg.default_endeavor_name + "\n" + read_file_str(user_path_obj.endeavor_file)
    debuglog = logging.getLogger('debuglog')
    debuglog.debug(f"endeavor_text: \n{endeavor_text}" )
    return [StoryDir(os.path.join(user_path_obj.endeavor_path, e_str))
            for e_str in endeavor_text.split()]

def path_join(p, f):
    """wrapper helps prevent module os from being needed in calling modules."""
    return os.path.join(p, f)

def mv_files_to_dir(fileList: List[str], dir: str)-> None:
    """
    verify that dir is actually a directory, and then move the list of files there,
    :param fileList:
    :param dir:
    :return:
    """
    if os.path.isdir(dir):
        pass
    else:
        raise NotADirectoryError

def read_file_str(filepath) -> str:
    """Read the file contents as a string if the file exists"""
    data = ""
    if os.path.isfile(filepath):
        with open(filepath, 'r') as data_file:
            data = data_file.read()
    return str(data)

def write_filepath(new_content, filepath):
    base_dir: str = os.path.dirname(filepath)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    new_fd: TextIO
    with open(filepath, "w") as new_fd:
        new_fd.write(new_content)

def remove_filepath(filepath: str):
    if os.path.exists(filepath):
        os.remove(filepath)

def write_dir_file(new_content, dir_name, doc_name):
    filepath = os.path.join(dir_name, doc_name)
    if os.path.isfile(filepath):
        previous_content = read_file_str(filepath)
        if previous_content == new_content:
            print(f"new content same as old. Nothing written. {doc_name}")
        else:
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


# class Endeavor_deprecated:
#     def __init__(self, name, a_user_path_obj):
#         self.name = name
#         self.dir_path = os.path.join(a_user_path_obj.endeavor_path, self.name)
#         self.story_list = get_file_names_by_pattern(self.dir_path, apCfg.story_pat)
#
#     def __str__(self):
#         return "Endeavor name:{} stories:{}".format(self.name, str(self.story_list))


class StoryDir:
    """
    loads a list of story files with full path info
    """
    def __init__(self, sdir):
        """
        Given a directory path, loads list of stories
        :param sdir: directory path
        """
        debuglog = logging.getLogger('debuglog')
        self.path = sdir
        self.story_list = []
        if os.path.isdir(sdir):
            dir_story_list = get_file_names_by_pattern(sdir, apCfg.story_pat)
            prioritized_file_list: str = get_file_names_by_pattern(sdir, apCfg.priority_pat)
            if prioritized_file_list:
                pri_file = prioritized_file_list[0]
                pri_order_text = read_file_str(pri_file) # take first if more than 1 pri file.
                pri_order_stories = pri_order_text.split("\n")
                for story_file in pri_order_stories: # add story files with listed priorities
                    story_file.strip()
                    if story_file != '':
                        full_story_path: str = os.path.join(sdir, story_file)
                        if os.path.isfile(full_story_path):
                            self.story_list.append(full_story_path)
                        else:
                            debuglog.warning(f"{story_file} is in {pri_file}, but not found in {sdir}")
            for story_file in dir_story_list: # add the dir stories not in pri_file
                if story_file not in self.story_list:
                    self.story_list.append(story_file)
        else:
            raise tlutil.TaskSourceException(f"{sdir} is not a directory, so can not be a StoryDir")


    def __str__(self):
        return "StoryDir:({}):".format(self.path) + ",".join(self.story_list)

if __name__ == "__main__":
    user_path_o: UserPaths = UserPaths()
    print(user_path_o.journal_path)

    if len(sys.argv) == 2 and sys.argv[1] == "init":
        os.makedirs(user_path_o.journal_path, exist_ok=True)



# print(dom + dayth_dict[dom])
