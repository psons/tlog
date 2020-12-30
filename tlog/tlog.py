#!/usr/local/bin/python3
"""
Composition: Top level application built of collections of TLDocument
Objects.  Stories read from Endeavor files, for example.
"""
from typing import List

from tldocument import TLDocument  # import re
from docsec import TLogInternalException, Item
import fileinput
from journaldir import StoryDir
import journaldir
# import sys
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

    def __init__(self, story_dir: StoryDir):
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
    return story_doc

def remove_item_from_story_file(item: Item) -> Item:
    """
    Remove item from it's file indicated by it's 'storySource:' attribute
    always log the item being removed.
    """
    tag = "write_item_to_story_file():"
    story_source  = item.get_item_attrib(StoryGroup.story_source_attr_name)
    if not story_source:
        logging.error(f"{tag} item to remove does not have a 'storySource:' attribute.")
        return None
    filepath = story_source
    story_tldoc: TLDocument= load_doc_from_file(filepath)
    story_tldoc.remove_document_item(item)
    journaldir.write_filepath(str(story_tldoc), filepath)


# todo test write_item_to_story_file()
def write_item_to_story_file(item: Item, default_file=None):
    """
    Writes an item into either its original storySource, or the default if provided.
    :param item: a task item to write.
    :param default_file: file path to write item into if there is no storySource in item
    :return: Story Document object that was written to disk
    """
    tag = "write_item_to_story_file():"
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
    story_tldoc: TLDocument= load_doc_from_file(filepath)
    story_tldoc.insert_update_document_item(item)
    journaldir.write_filepath(str(story_tldoc), filepath)
    return story_tldoc


# def write_back_updated_story(item: Item):
#     """
#     todo: this only has a test call, and one that is commented out in main() get rid of it in favor of write_item_to_story_file()
#     :param item: a task item to write to it's StorySource
#     :return: Story Document object that was written to disk
#     """
#     story_source  = item.get_item_attrib(StoryGroup.story_source_attr_name)
#     if story_source is None:
#         raise TLogInternalException(
#             f"Can not write_back_updated_story() for ({item.top}). missing {StoryGroup.story_source_attr_name}")
#     else:
#         filepath = story_source
#     story_doc = load_doc_from_file(filepath)
#     story_doc.insert_update_document_item(item)
#     journaldir.write_filepath(str(story_doc), filepath)
#     return story_doc

def find_prev_journal_dir(latest_dir, history_months):
    file_count = 0
    dirs_to_search = history_months
    next_search_dir = latest_dir
    search_dir = latest_dir
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


# def sj_file_list_by_dir(latest_dir, history_months):
#     """
#     get group of story files and latest journal file name lists given dir
#     if none are found in the latest_dir, search back up to history_months
#     until at least 1 file is found.
#     :param latest_dir: current journaldir to look back in history from to find files.
#     :param history_months: limit on how far back to search
#     :return: list of story files, list of journal files, and the dir they were found.
#     """
#     file_count = 0
#     dirs_to_search = history_months
#     next_search_dir = latest_dir
#     while file_count == 0 and dirs_to_search > 0:
#         search_dir = next_search_dir
#         sfl = journaldir.get_file_names_by_pattern(
#             search_dir, journaldir.story_pat)
#         jfl = journaldir.get_file_names_by_pattern(
#             search_dir, journaldir.journal_pat)
#         file_count = len(sfl) + len(jfl)
#         print("{} stories and {} journals in {}".
#               format(len(sfl), len(jfl), search_dir))
#         next_search_dir = journaldir.get_prior_dir(search_dir)  # can return None
#         if not next_search_dir:
#             dirs_to_search = 0  # loop to end if no sensible search_dir
#         else:
#             dirs_to_search -= 1
#
#     jfl = jfl[-1:]  # just the last journal file in the list
#     return sfl, jfl, search_dir


def load_doc_from_file(file_name) -> TLDocument:
    file_text = journaldir.read_file_str(file_name)
    return TLDocument.fromtext(file_text)

# todo test various short_copy cases. -->  need for short copy may be changing.
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
        self.ulog.setLevel(logging.DEBUG) # should support command line option tro set, and default to INFO
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

def early_debug_exit(message: str) -> None:
    print(f'EARLY DEBUG EXIT {message}')
    exit(99)



def main():
    """
    Requires no command line arguments, but may use them to interpret the user environment differently.
    User environment includes directories of story files with tasks, which will be read into lists of stories.
        See Tlog User Documentation.md

    1. build the "old" journal / to do (j/td) file.
    2. make_scrum_resolved() as:
        a. start with the existing resolved file add to new j/td scrum object as resolved.
        b. extract '/ -' in-progress from old j/td.  Flip them to 'u -'. add them to new j/td scrum object as resolved.
        c. extract 'x -' completed tasks from old j/td.  Add them to new j/td scrum object as resolved
            todo need about 5 test cases for item.add_item_merge_enhanced(self, other_item):
    3. Persist the scrum resolved_data.  (important because a later step will remove 'x -' from stories.)
    4. Write everything in old j/td back to Endeavor stories on disk, merging according to the write_item_to_story_file() call to
        insert_update_document_item(item) merge the backlog into the journal.
    5. Git commit the updates, which will include tasks updated to 'x -' and 'a -'.
    6. Remove resolved items from stories using remove_item_from_story_file(r_item).  Resolved items have been
       flagged as 'x -' or 'a -' in j/td by a user.

    7. Read the Endeavor stories according to load_endeavor_stories(user_path_o) (now including the old j/td tasks)
        - eventually the stores in the endeavors will be prioritized.  There is a story for that.
    8. Shorten the stories to max tasks in each.  Build a sprint candidate list (short backlog list)
        of task items from the stories.
    9. Pop the global sprint size number of stories off the backlogs of list. Add them to new j/td scrum object as todo.
    10. Persist the scrum todo_data
    11. Git commit the updates, which will have both parts of the new scrum and the updated Endeavor stories with
        resolved items now removed. ( they are flagged as resolved in stories in the previous commit)
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
    old_jtd_doc = TLDocument(day=daily_o.domth)
    story_task_document = TLDocument() # this becomes the to-do.md file
    story_task_document.doc_name = "Endeavor story tasks based on" + user_path_o.endeavor_file
    look_back_months = 24
    cmd_line_story_docs = []
    journal_story_docs = []

    # ############################
    # Gather input state from Disk and command line
    # ============================
    ## look at cmd line args and find the to do doc
    # if len(sys.argv) < 2:
    journaldir.init(my_journal_dir)
    # look back in history to find past journal dir will not be necessary with 'to-do' replaces journal, and
    # FollowUpQueue/FollowUp story.md replaces past journals from prior months or years.
    prev_journal_dir = find_prev_journal_dir(my_journal_dir, look_back_months)
    story_dir_o = StoryDir(prev_journal_dir)
    journal_story_docs = StoryGroup(story_dir_o).get_short_stories() # * story.md docs.
    j_file_list = journaldir.get_file_names_by_pattern(
        story_dir_o.path, journaldir.journal_pat) # journal {date].md files
    msg = "no argument sfile_list: " + ",".join(story_dir_o.story_list)
    # section above will be eliminated in favor of the FollowUpQueue/FollowUp story.md to be read farther down in code.

    msgr.screen_log(tag, msg)
    msgr.screen_log(tag, "no argument jfile_list:" + ",".join(j_file_list))
    # I don't want to support any command line features now other
    # else:
    #     # usage: tlog jdir some_path_to_a_dir
    #     if sys.argv[1] in supported_commands:
    #         tlog_command = sys.argv[1]
    #         if tlog_command == "jdir":
    #             # This feature should be enhanced to support endeavors.
    #             #  Should I change from default user_path_o?
    #             my_journal_dir = sys.argv[2] # the actual dated jdir the user wants to use
    #             # todo should just get to-do file from the alternate dir
    #             journal_story_docs = StoryGroup(StoryDir(my_journal_dir)).get_short_stories()
    #             #   the original location will be kept as the story source.
    #             j_file_list = journaldir.get_file_names_by_pattern(
    #                             my_journal_dir, journaldir.journal_pat)
    #             # s_file_list, j_file_list, prev_journal_dir = sj_file_list_by_dir(my_journal_dir, look_back_months)
    #             # todo fix this: print("jdir argument file_list:", tlog_command, s_file_list, j_file_list)
    #         else:
    #             raise TLogInternalException("A supported command has no implementation")
    #     else:
    #         # should regular journaldir and Endeavor behavior be included?
    #         # user has not provided a command arg, so treat the arguments as a list of story files to pull tasks from.
    #         #   the original location will be kept as the story source.
    #         # todo test cmd line stories
    #         # these stories are not shortened to max tasks.  Think about the use case should they be?
    #         s_file_list = sys.argv[1:]
    #         cmd_line_story_docs = [load_doc_from_file(s_file) for s_file in s_file_list]
    #         j_file_list = []
    #         msgr.screen_log(tag, "(re) initializing Journal from stories:" + ",".join(s_file_list))

    # load the latest journal into the journal for today
    last_journal = j_file_list[-1] if j_file_list else None
    old_jtd_doc.add_lines(fileinput.input(last_journal))

    resolved_doc: TLDocument = load_doc_from_file( journaldir.path_join(daily_o.jdir, daily_o.cday_resolved_fname))
    new_jtd_doc: TLDocument =  TLDocument()
    new_jtd_doc.add_section_list_items_to_scrum(resolved_doc.journal) # items in resolved file from earlier today run of tlog

    in_progress_items = old_jtd_doc.select_all_section_items_by_pattern(TLDocument.in_progress_pat) # items in old jtd that are in progress
    unfinished_item_copies = [ item.deep_copy(TLDocument.top_parser_pat) for item in in_progress_items ]
    [ item.modify_item_top(TLDocument.in_progress_pat, TLDocument.unfinished_s) for item in unfinished_item_copies ] # toggle in progress to unfinished
    new_jtd_doc.add_list_items_to_scrum(unfinished_item_copies)

    resolved_items = old_jtd_doc.select_all_section_items_by_pattern(TLDocument.resolved_pat) # items in jtd that are resolved (xa)
    new_jtd_doc.add_list_items_to_scrum(resolved_items)


    print(f"resolved_doc: {resolved_doc}")
    print(f"new_jtd_doc.scrum: {new_jtd_doc.scrum}")
    resolved_data = str(new_jtd_doc.scrum.head_instance_dict[new_jtd_doc.resolved_section_head])
    # do I stil want the resolved to have a header as follows? :     "## " + daily_o.domth
    journaldir.write_dir_file(resolved_data + '\n', daily_o.jdir, daily_o.cday_resolved_fname)

    # write all the tasks from the old jtd
    for story_item in old_jtd_doc.get_backlog_list():
        write_item_to_story_file(story_item, user_path_o.new_task_story_file)

    user_path_o.git_add_all(daily_o, f"data written to stories and resolved file from {last_journal}")

    # 6. Remove resolved items from stories using remove_item_from_story_file(r_item).
    # todo debut checkout this next line with some resolved items with a 'storySource:' to see if they get removed.
    [remove_item_from_story_file(r_item) for r_item in resolved_items]

    # 7. Read the Endeavor stories according to load_endeavor_stories(user_path_o) (now including the old j/td tasks)
    story_dir_objects: List[StoryDir] = journaldir.load_endeavor_stories(user_path_o)
    # 8. Shorten the stories to max tasks in each.  Build a sprint candidate list (short backlog list)
    #    of task items from the stories.
    endeavor_story_docs: List[TLDocument] = [story_doc for sdo in story_dir_objects
                                             for story_doc in StoryGroup(sdo).get_short_stories()]
    # At this point the short_stories have the short list of tasks in the 'backlog' section of each Doc.
    # They really are 'sprint candidates': the top tasks in each story that may get into the day sprint.
    # Picking off the top 3 stories will always take from the top endeavor
    #       (if they are written in priority order)
    # however the stories within an endeavor are just in file listing order.
    # (see tlog story 'Prioritized Backlog story.txt'
    short_s_doc_list =  journal_story_docs + endeavor_story_docs + cmd_line_story_docs
    msgr.ulog.info("trimmed story docs: " + str_o_list(short_s_doc_list, delimiter="\nStory:\n", prefix_delim=True))


    # 9. Pop the global sprint size number of stories off the backlog list. Add them to new j/td scrum object as todo.

    early_debug_exit(f"new_jtd_doc: {new_jtd_doc}")


    old_jtd_doc.merge_backlog(story_task_document.backlog)
    # old_jtd_doc.make_scrum()


    # todo then stop adding tasks in the merge if capacity will be exceeded.(already added support for a task capacity in TLDocument.)
    # load merge all the story tasks into one document
    for short_story_doc in short_s_doc_list:
        story_task_document.merge_backlog(short_story_doc.backlog)

    story_task_document.generate_backlog_title_hashes()  # set the title hashes on tasks for change detection

    # don't need this if I make_scrum() correctly and write it later. see resolved_data adf todo_data below.
    # xa_story_items = old_jtd_doc.\
    #     get_xa_story_tasks(StoryGroup.story_source_attr_name) # uses the scrum

    # dont need if make_scrum per above
    # for xa_story_item in xa_story_items:
    #     write_item_to_story_file(xa_story_item, default_file=user_path_o.new_task_story_file)
    #     # replacing with above write_back_updated_story(xa_story_item)
    # # prevent whole previous month text from rolling to new month

    # todo might not need this after converting to daily scrum.
    if my_journal_dir != prev_journal_dir:
        msgr.screen_log(tag, "Will drop journal because it is from a back month")
        old_jtd_doc.drop_journal()

    # write the daily journal doc
    old_jtd_doc.doc_name = daily_o.cday_journal_fname
    journaldir.write_dir_file(str(old_jtd_doc.scrum) + '\n',
                              daily_o.jdir, old_jtd_doc.doc_name)

    todo_data = str(old_jtd_doc.scrum.head_instance_dict[old_jtd_doc.todo_section_head])
    journaldir.write_dir_file(todo_data + '\n', daily_o.jdir, daily_o.cday_todo_fname)

if __name__ == "__main__":
    main()

