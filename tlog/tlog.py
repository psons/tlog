#!/usr/local/bin/python3
"""
Composition: Top level application built of collections of TLDocument
Objects.  Stories read from Endeavor files, for example.

First, read and classify each input line as one or more of:
 - a mark down heading for a new Section
 - a task line to create a new Item to add to the list under the 
   current Section
 - text to put under the current Item
 - a "do" task Item to be put in the backlog Section
Then Print out the list of Sections in order with the 
backlog Section at the end 

See tlmodel module journal_documentation for pattern_strs that classify input
lines
"""
from typing import List

from tldocument import TLDocument  # import re
from docsec import TLogInternalException, Item
import fileinput
import journaldir
import sys
import logging


# import markdown # avoid html support and coupling to markdown for now

class StoryGroup:
    """
    Adds story sematics around a group of Documents read from files in a directory
	Combines the journaldir.StoryDir and the tlmodel.Document to get
	a collection of tasks.
	Sets attributes in the tasks in the Documents to allow changes in the tasks in the
	    storySource: endeavor/story
	journal to be written back to the original stories
	"""

    story_source_attr_name = "storySource"

    def __init__(self, story_dir: journaldir.StoryDir):
        self.story_dir = story_dir
        self.story_docs = [load_story_from_file(s_file)
                           for s_file in self.story_dir.story_list]

    def __str__(self):
        return "\n".join([str(d) for d in self.story_docs])

    def get_short_stories(self):
        """return list of stories shortened to maxTasks Items"""
        return [short_copy(sd) for sd in self.story_docs]


def load_story_from_file(file_name):
    """adds story attribution around a Doc from file"""
    story_doc = load_doc_from_file(file_name)
    story_doc.attribute_all_backlog_items(StoryGroup.story_source_attr_name, file_name)
    return story_doc

# todo test write_back_updated_story
def write_back_updated_story(item: Item):
    story_source  = item.get_item_attrib(StoryGroup.story_source_attr_name)
    if story_source is None:
        raise TLogInternalException(
            f"Can not write_back_updated_story() for ({item.top}). missing {StoryGroup.story_source_attr_name}")
    else:
        filepath = story_source
    story_doc = load_doc_from_file(filepath)
    story_doc.update_journal_item(item, Item.title_hash_attr_str)
    journaldir.write_filepath(str(story_doc), filepath)
    return story_doc

def find_prev_journal_dir(latest_dir, history_months):
    file_count = 0
    dirs_to_search = history_months
    next_search_dir = latest_dir
    while file_count == 0 and dirs_to_search > 0:
        search_dir = next_search_dir
        sfl = journaldir.get_file_names_by_pattern(
            search_dir, journaldir.story_pat)
        jfl = journaldir.get_file_names_by_pattern(
            search_dir, journaldir.journal_pat)
        file_count = len(sfl) + len(jfl)
        print("{} stories and {} journals in {}".
              format(len(sfl), len(jfl), search_dir))
        next_search_dir = journaldir.get_prior_dir(search_dir)  # can return None
        if not next_search_dir:
            dirs_to_search = 0  # loop to end if no sensible search_dir
        else:
            dirs_to_search -= 1

    return search_dir


# todo break this into 3 calls (1) return the dir with files, (2) load it as a StoryGroup, and (3) load journal docs
def sj_file_list_by_dir(latest_dir, history_months):
    """
    get group of story files and latest journal file name lists given dir
    if none are found in the latest_dir, search back up to history_months
    until at least 1 file is found.
    :param latest_dir: current journaldir to look back in history from to fine files.
    :param history_months: limit on how far back to search
    :return: list of story files, list of journal files, and the dir they were found.
    """
    file_count = 0
    dirs_to_search = history_months
    next_search_dir = latest_dir
    while file_count == 0 and dirs_to_search > 0:
        search_dir = next_search_dir
        sfl = journaldir.get_file_names_by_pattern(
            search_dir, journaldir.story_pat)
        jfl = journaldir.get_file_names_by_pattern(
            search_dir, journaldir.journal_pat)
        file_count = len(sfl) + len(jfl)
        print("{} stories and {} journals in {}".
              format(len(sfl), len(jfl), search_dir))
        next_search_dir = journaldir.get_prior_dir(search_dir)  # can return None
        if not next_search_dir:
            dirs_to_search = 0  # loop to end if no sensible search_dir
        else:
            dirs_to_search -= 1

    jfl = jfl[-1:]  # just the last journal file in the list
    return sfl, jfl, search_dir


def load_doc_from_file(file_name):
    file_text = journaldir.read_file_str(file_name)
    return TLDocument.fromtext(file_text)


# todo WTF is in_progres with only one 's'?

# todo test various short_copy cases.
def short_copy(long_story_doc):
    """copy the long_story_doc arg and shorten to only maxTasks,
    making sure '/ -' tasks + 'd - ' tasks is less than maxTasks
    """
    short_doc = TLDocument.fromtext(str(long_story_doc))
    doc_max_tasks: int
    if long_story_doc.max_tasks:
         doc_max_tasks = int(long_story_doc.max_tasks)
    else:
        doc_max_tasks = TLDocument.default_maxTasks
    short_doc.make_in_progress()
    short_doc.shorten_in_progress()
    remaining_tasks_allowed = doc_max_tasks - len(short_doc.in_progress.body_items)
    if remaining_tasks_allowed < 0:
        remaining_tasks_allowed = 0
    short_doc.shorten_backlog(remaining_tasks_allowed)
    return short_doc

# todo redo extend logging.Logger to add the specifics, and the screen lo method.
#  alternately, add a custom level that is for just writing user prompts to the
#  screen.
class Messaging:
    def __init__(self, lname, info_file, debug_file):
        self.ulog = logging.getLogger(lname)
        self.ulog.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        user_handler = logging.FileHandler(info_file)
        user_handler.setLevel(logging.INFO)
        user_handler.setFormatter(formatter)
        self.ulog.addHandler(user_handler)

        programmer_handler = logging.FileHandler(debug_file)
        programmer_handler.setLevel(logging.DEBUG)
        programmer_handler.setFormatter(formatter)
        self.ulog.addHandler(programmer_handler)


    def screen_log(self, tag, msg):
        print(msg)
        self.ulog.info(tag + msg)




def str_o_list(in_list: List, delimiter=",", prefix_delim=False):
    str_list = [str(o) for o in in_list]
    r_str = delimiter.join(str_list)
    if prefix_delim:
        r_str = delimiter + r_str
    return r_str

supported_commands = ["jdir"]
"""
jdir - treat the next argument to tlog as the journal_dir.
"""


def main():
    tag = "tlog main:"
    daily_o = journaldir.Daily()
    msgr = Messaging('user', daily_o.info_log_file, daily_o.debug_log_file)
    msgr.screen_log(tag, f"logging to: {daily_o.info_log_file}")
    msgr.ulog.info(f"run start: {daily_o.dt}")
    msgr.ulog.debug(tag + str(daily_o))
    my_journal_dir = daily_o.jdir
    user_path_o = journaldir.UserPaths()
    user_path_o.git_init_journal()
    journal_document = TLDocument(day=daily_o.domth)
    story_task_document = TLDocument()
    story_task_document.doc_name = "Endeavor story tasks based on" + user_path_o.endeavor_file
    look_back_months = 24
    cmd_line_story_docs = []
    journal_story_docs = []
    if len(sys.argv) < 2:
        journaldir.init(my_journal_dir)
        prev_journal_dir = find_prev_journal_dir(my_journal_dir, look_back_months)
        story_dir_o = journaldir.StoryDir(prev_journal_dir)
        journal_story_docs = StoryGroup(story_dir_o).get_short_stories()
        j_file_list = journaldir.get_file_names_by_pattern(
            story_dir_o.path, journaldir.journal_pat)
        msg = "no argument sfile_list: " + ",".join(story_dir_o.story_list)
        msgr.screen_log(tag, msg)
        msgr.screen_log(tag, "no argument jfile_list:" + ",".join(j_file_list))
    else:
        if sys.argv[1] in supported_commands:
            tlog_command = sys.argv[1]
            if tlog_command == "jdir":
                # This feature needs work to support endeavors.
                #  Should I change from default user_path_o?
                my_journal_dir = sys.argv[2] # the actual dated jdir the user wants to use
                journal_story_docs = StoryGroup(journaldir.StoryDir(
                                my_journal_dir)).get_short_stories()
                j_file_list = journaldir.get_file_names_by_pattern(
                                my_journal_dir, journaldir.journal_pat)
                # s_file_list, j_file_list, prev_journal_dir = sj_file_list_by_dir(my_journal_dir, look_back_months)
                # todo fix this: print("jdir argument file_list:", tlog_command, s_file_list, j_file_list)
            else:
                raise TLogInternalException("A supported command has no implementation")
        else:
            # todo test cmd line stories
            s_file_list = sys.argv[1:]
            cmd_line_story_docs = [load_doc_from_file(s_file) for s_file in s_file_list]
            j_file_list = []
            msgr.screen_log(tag, "(re) initializing Journal from stories:" + ",".join(s_file_list))

    # get the trimmed story docs from endeavors
    story_dir_objects = journaldir.load_endeavor_stories(user_path_o)
    endeavor_story_docs: List[TLDocument] = [story_doc for sdo in story_dir_objects
                                             for story_doc in StoryGroup(sdo).get_short_stories()]

    short_s_doc_list = cmd_line_story_docs + journal_story_docs + endeavor_story_docs
    msgr.ulog.info("trimmed story docs: " + str_o_list(short_s_doc_list, delimiter="\nStory:\n", prefix_delim=True))

    # load merge all the story tasks into one document
    for short_story_doc in short_s_doc_list:
        story_task_document.merge_backlog(short_story_doc.backlog)

    # set the title hashes on tasks for change detection
    story_task_document.generate_backlog_title_hashes()

    # load the latest journal into the journal for today
    last_journal = j_file_list[-1] if j_file_list else None
    journal_document.add_lines(fileinput.input(last_journal))
    # for in_document_file in j_file_list:
    #     journal_document.add_lines(fileinput.input(in_document_file))
    journal_document.make_in_progress("## " + daily_o.domth)
    journal_document.merge_backlog(story_task_document.backlog)
    journal_document.make_scrum()
    write_back_xa_story_items = journal_document.\
        get_xa_story_tasks(StoryGroup.story_source_attr_name) # uses the scrum

    for xa_story_item in write_back_xa_story_items:
        write_back_updated_story(xa_story_item)
    # prevent whole previous month text from rolling to new month
    # todo might not need this after converting to daily scrum.
    if my_journal_dir != prev_journal_dir:
        screen_log(tag, "Will drop journal because it is from a back month")
        journal_document.drop_journal()


    user_path_o.git_add_all()

    journal_document.doc_name = daily_o.cday_fname
    # write the daily journal doc
    journaldir.write_dir_file(str(journal_document.scrum) + '\n',
                              daily_o.jdir, journal_document.doc_name)


if __name__ == "__main__":
    main()

