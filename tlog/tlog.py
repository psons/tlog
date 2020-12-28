#!/usr/local/bin/python3
"""
Composition: Top level application built of collections of TLDocument
Objects.  Stories read from Endeavor files, for example.
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
    Adds story semantics around a group of Documents read from files in a directory
	Combines the journaldir.StoryDir and the tlmodel.Document to get
	a collection of tasks.
	Sets attributes in the tasks in the Documents to allow changes in the tasks to be written back to the
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
    story_doc: TLDocument = load_doc_from_file(file_name)
    story_doc.attribute_all_backlog_items(StoryGroup.story_source_attr_name, file_name)
    story_doc.for_journal_sections_add_all_missing_item_title_hash()
    # todo write back story with titleHashes and storySources
    return story_doc

# todo. x - implement this
# todo / -  and use it instead of write_back_updated_story
def write_story_file(item: Item, default_file=None):
    """
    Writes an item into either its original storySource, or the default if provided.
    :param item: a task item to write.
    :param default_file: file path to write item into if there is no storySource in item
    :return: Story Document object that was written to disk
    """
    tag = "write_story_file():"
    story_source  = item.get_item_attrib(StoryGroup.story_source_attr_name)
    filepath = default_file
    if story_source:
        filepath = story_source
    else:
        if default_file:
            item.set_attrib(StoryGroup.story_source_attr_name, default_file)
        else:
            raise TLogInternalException(
                f"{tag} Do not have file to write to for ({item.top}). missing {StoryGroup.story_source_attr_name}"
                f"and no default has been provided")

    # get the story contents from disk and insert / update the item.
    story_tldoc = load_doc_from_file(filepath)
    story_tldoc.insert_update_journal_item(item)
    journaldir.write_filepath(str(story_tldoc), filepath)
    return story_tldoc


# todo test write_back_updated_story
def write_back_updated_story(item: Item):
    """
    todo: this only has a test call, and one that is commented out in main()
    :param item: a task item to write to it's StorySource
    :return: Story Document object that was written to disk
    """
    story_source  = item.get_item_attrib(StoryGroup.story_source_attr_name)
    if story_source is None:
        raise TLogInternalException(
            f"Can not write_back_updated_story() for ({item.top}). missing {StoryGroup.story_source_attr_name}")
    else:
        filepath = story_source
    story_doc = load_doc_from_file(filepath)
    story_doc.insert_update_journal_item(item)
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
    :param latest_dir: current journaldir to look back in history from to find files.
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


def load_doc_from_file(file_name) -> TLDocument:
    file_text = journaldir.read_file_str(file_name)
    return TLDocument.fromtext(file_text)

# todo test various short_copy cases.
def short_copy(long_story_doc):
    """copy the long_story_doc arg and shorten to only maxTasks,
    making sure the number of '/ -' tasks + 'd - ' tasks is less than maxTasks
    """
    short_doc = TLDocument.fromtext(str(long_story_doc))
    doc_max_tasks: int
    if long_story_doc.max_tasks:
         doc_max_tasks = int(long_story_doc.max_tasks)
    else:
        doc_max_tasks = TLDocument.default_maxTasks
    short_doc.make_in_progress()
    short_doc.shorten_in_progress()
    num_in_progress = short_doc.in_progress.get_num_items()
    remaining_tasks_allowed = doc_max_tasks - num_in_progress
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
    """
    Like 'join()' but optionally print leading delimiter
    :param in_list: List of objects to call str() on.
    :param delimiter:
    :param prefix_delim:
    :return:
    """
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
    """
    Requires no command line arguments, but may use them to interpret the user environment differently.
    User environment includes directories of story files with tasks, which will be read into lists of stories.
        See Tlog User Documentation.md

    The lists of stories will be loaded into a special section of a TLDocument object called the 'backlog'
    (as in 'Scrum' vernacular).  in each Story, the 'maxTasks:' attribute constrains what is read into the backlog,
    making it really represent a set of 'sprint candidate' tasks. todo refactor to rename 'backlog' to 'sprint'

    Tasks are to be kept in priority order in a stories, and hence when endeavors are also in priority order,
    the sprint will be in priority order. todo implement a story that prioritizes endeavors.


    """
    # initialize everything
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
    story_task_document = TLDocument() # this becomes the to-do.md file
    story_task_document.doc_name = "Endeavor story tasks based on" + user_path_o.endeavor_file
    look_back_months = 24
    cmd_line_story_docs = []
    journal_story_docs = []

    # ############################
    # Gather input state from Disk and command line
    # ============================
    ## look at cmd line args and find the todo doc
    if len(sys.argv) < 2:
        journaldir.init(my_journal_dir)
        # look back in history to find past journal dir will not be necessary with 'to-do' replaces journal, and
        # FollowUpQueue/FollowUp story.md replaces past journals from prior months or years.
        prev_journal_dir = find_prev_journal_dir(my_journal_dir, look_back_months)
        story_dir_o = journaldir.StoryDir(prev_journal_dir)
        journal_story_docs = StoryGroup(story_dir_o).get_short_stories()
        j_file_list = journaldir.get_file_names_by_pattern(
            story_dir_o.path, journaldir.journal_pat)
        msg = "no argument sfile_list: " + ",".join(story_dir_o.story_list)
        # section above will be eliminated in favor of the FollowUpQueue/FollowUp story.md to be read farther down in code.

        msgr.screen_log(tag, msg)
        msgr.screen_log(tag, "no argument jfile_list:" + ",".join(j_file_list))
        # todo: rename this should be the to-do file.  do all the write back to stories processing.
    else:
        # usage: tlog jdir some_path_to_a_dir
        if sys.argv[1] in supported_commands:
            tlog_command = sys.argv[1]
            if tlog_command == "jdir":
                # This feature should be enhanced to support endeavors.
                #  Should I change from default user_path_o?
                my_journal_dir = sys.argv[2] # the actual dated jdir the user wants to use
                # todo should just get to-do file from the alternate dir
                journal_story_docs = StoryGroup(journaldir.StoryDir(
                                my_journal_dir)).get_short_stories()
                j_file_list = journaldir.get_file_names_by_pattern(
                                my_journal_dir, journaldir.journal_pat)
                # s_file_list, j_file_list, prev_journal_dir = sj_file_list_by_dir(my_journal_dir, look_back_months)
                # todo fix this: print("jdir argument file_list:", tlog_command, s_file_list, j_file_list)
            else:
                raise TLogInternalException("A supported command has no implementation")
        else:
            # user has not provided a command arg, so treat the arguments as a list of story files.
            # todo test cmd line stories
            # these stories are not shortened to max tasks.  Think about the use case should they be?
            s_file_list = sys.argv[1:]
            cmd_line_story_docs = [load_doc_from_file(s_file) for s_file in s_file_list]
            j_file_list = []
            msgr.screen_log(tag, "(re) initializing Journal from stories:" + ",".join(s_file_list))

    # get the story docs from endeavors
    story_dir_objects = journaldir.load_endeavor_stories(user_path_o)

    #### UPDATE JOURNAL TO DO BACK TO STORIES FROM DISK.
    #### beginning of new sprint creation. this has to be after the journal updates have been injected into the FULL BACKLOG and pushed back to source story objects.
    ####        either (yes) write to disk and re-read it, or (no) find the original TLDocs in memory some how. an Item could have a ref to the parent story
    #### only after the updates are done and written to disk, can we go through and shorten stories to 'maxTasks' to build the sprint candidate list.

    #### THEN RE-READ ALLTHE STORIES AND SHORTEN THEM AND GENERATE A NEW SPRINT.

    # trim the story lists to maxTasks
    endeavor_story_docs: List[TLDocument] = [story_doc for sdo in story_dir_objects
                                             for story_doc in StoryGroup(sdo).get_short_stories()]

    # At this point the short_stories have the short list of tasks in the 'backlog' section of each Doc.
    # They really are 'sprint candidates': the top tasks in each story that may get into the day sprint.
    # Picking off the top 3 stories will always take from the top endeavor
    #       (if they are written in priority order)
    # however the stories within an endeavor are just in file listing order.
    # (see tlog story 'Prioritized Backlog story.txt'
    short_s_doc_list = cmd_line_story_docs + journal_story_docs + endeavor_story_docs
    msgr.ulog.info("trimmed story docs: " + str_o_list(short_s_doc_list, delimiter="\nStory:\n", prefix_delim=True))

    # todo then stop adding tasks in the merge if capacity will be exceeded.(already added support for a task capacity in TLDocument.)
    # load merge all the story tasks into one document
    for short_story_doc in short_s_doc_list:
        story_task_document.merge_backlog(short_story_doc.backlog)

    story_task_document.generate_backlog_title_hashes()  # set the title hashes on tasks for change detection

    # load the latest journal into the journal for today
    last_journal = j_file_list[-1] if j_file_list else None
    journal_document.add_lines(fileinput.input(last_journal))
    journal_document.make_in_progress("## " + daily_o.domth)
    journal_document.merge_backlog(story_task_document.backlog)
    journal_document.make_scrum()
    xa_story_items = journal_document.\
        get_xa_story_tasks(StoryGroup.story_source_attr_name) # uses the scrum

    # todo: write all the tasks from the journal ( tasks from journal_story_docs ) using write_story_file()
    #   write_story_file will pt them
    #   the journal evolves to become the to do.md file in a next step.
    for story_item in journal_document.get_backlog_list():
        write_story_file(story_item, user_path_o.new_task_story_file)

    # todo: 2020-12-20 write_xa
    # for xa_story_item in xa_story_items:
    #     write_story_file(xa_story_item, default_file=user_path_o.new_task_story_file)
    #     # replacing with above write_back_updated_story(xa_story_item)
    # # prevent whole previous month text from rolling to new month

    # todo might not need this after converting to daily scrum.
    if my_journal_dir != prev_journal_dir:
        msgr.screen_log(tag, "Will drop journal because it is from a back month")
        journal_document.drop_journal()


    user_path_o.git_add_all()

    # write the daily journal doc
    journal_document.doc_name = daily_o.cday_journal_fname
    journaldir.write_dir_file(str(journal_document.scrum) + '\n',
                              daily_o.jdir, journal_document.doc_name)

    resolved_data = str(journal_document.scrum.head_instance_dict[journal_document.resolved_section_head])
    todo_data = str(journal_document.scrum.head_instance_dict[journal_document.todo_section_head])
    journaldir.write_dir_file(resolved_data + '\n', daily_o.jdir, daily_o.cday_resolved_fname)
    journaldir.write_dir_file(todo_data + '\n', daily_o.jdir, daily_o.cday_todo_fname)

if __name__ == "__main__":
    main()

