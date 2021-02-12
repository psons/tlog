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
        self.story_docs: List[TLDocument] = [load_and_resave_story_file_with_attribs(s_file)
                                             for s_file in self.story_dir.story_list]

    def __str__(self):
        return "\n".join([str(d) for d in self.story_docs])


def load_and_resave_story_file_with_attribs(file_name) -> TLDocument:
    """
    adds 'storySource:' and 'titleHash:' to each item in a doc from file and saves it back to disk.
    These attributes enable items tro be re titled and still update the original story item.
    """
    story_doc: TLDocument = load_doc_from_file(file_name)
    story_doc.attribute_all_unresolved_items(StoryGroup.story_source_attr_name, file_name)
    story_doc.for_journal_sections_add_all_missing_item_title_hash()
    journaldir.write_filepath(str(story_doc), file_name)
    return story_doc

def remove_item_from_story_file(item: Item) -> Item:
    """
    Remove item from it's file indicated by it's 'storySource:' attribute
    always log the item being removed.
    """
    tag = "write_item_to_story_file():"
    story_source  = item.get_item_attrib(StoryGroup.story_source_attr_name)
    if not story_source:
        logging.warning(f"{tag} item to remove does not have a 'storySource:' attribute.")
        return None
    filepath = story_source
    story_tldoc: TLDocument= load_doc_from_file(filepath)
    story_tldoc.remove_document_item(item)
    journaldir.write_filepath(str(story_tldoc), filepath)


# todo test write_item_to_story_file()
def write_item_to_story_file(item: Item, default_file=None, new_item_section_head: str = "# Added Tasks"):
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
    story_tldoc.insert_update_document_item(item, new_item_section_head)
    journaldir.write_filepath(str(story_tldoc), filepath)
    return story_tldoc


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


def load_doc_from_file(file_name) -> TLDocument:
    file_text = journaldir.read_file_str(file_name)
    return TLDocument.fromtext(file_text)

# todo redo extend logging.Logger to add the specifics, and the screen log method.
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
    9. Pop the global sprint size number of stories off the backlogs of list. Add them to new j/td scrum object as to do.
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
    look_back_months = 24

    # ############################
    # Gather input state from Disk and command line
    # ============================

    # --- might be influenced by command line at some point.
    #     1. build the "old" journal / to do (j/td) file.
    journaldir.init(my_journal_dir)
    journaldir.init(journaldir.join(user_path_o.endeavor_path, journaldir.default_endeavor_name))
    # look back in history to find past journal dir
    prev_journal_dir = find_prev_journal_dir(my_journal_dir, look_back_months)
    story_dir_o = StoryDir(prev_journal_dir)

    journal_story_docs = StoryGroup(story_dir_o).story_docs # * story.md docs.
    j_file_list = journaldir.get_file_names_by_pattern(
        story_dir_o.path, journaldir.journal_pat) # journal {date].md files
    msg = "no argument sfile_list: " + ",".join(story_dir_o.story_list)
    # ---

    msgr.screen_log(tag, msg)
    msgr.screen_log(tag, "no argument jfile_list:" + ",".join(j_file_list))
    # I don't want to support any command line features now other
    #     if sys.argv[1] in supported_commands:

    #
    # load the latest journal into the journal for today
    last_journal = "no_journal_yet"
    if len(j_file_list) > 0:
        last_journal = j_file_list[-1]
        # old_jtd_doc = load_and_resave_story_file_with_attribs(last_journal)
        old_jtd_doc.add_lines(fileinput.input(last_journal))

    #     2. make_scrum_resolved() as:
    #         a. start with the existing resolved file add to new j/td scrum object as resolved.
    #         b. extract '/ -' in-progress from old j/td.  Flip them to 'u -'. add them to new j/td scrum object as resolved.
    #         c. extract 'x -' completed tasks from old j/td.  Add them to new j/td scrum object as resolved

    resolved_doc: TLDocument = load_doc_from_file( journaldir.path_join(daily_o.jdir, daily_o.cday_resolved_fname))
    new_jtd_doc: TLDocument =  TLDocument()
    new_jtd_doc.add_section_list_items_to_scrum(resolved_doc.journal) # items in resolved file from earlier today run of tlog

    in_progress_items = old_jtd_doc.select_all_section_items_by_pattern(TLDocument.in_progress_pat) # items in old jtd that are in progress
    unfinished_item_copies = [ item.deep_copy(TLDocument.top_parser_pat) for item in in_progress_items ]
    [ item.modify_item_top(TLDocument.in_progress_pat, TLDocument.unfinished_s) for item in unfinished_item_copies ] # toggle in progress to unfinished
    new_jtd_doc.add_list_items_to_scrum(unfinished_item_copies)

    resolved_items = old_jtd_doc.select_all_section_items_by_pattern(TLDocument.resolved_pat) # items in jtd that are resolved (xa)
    new_jtd_doc.add_list_items_to_scrum(resolved_items)

    #     3. Persist the scrum resolved_data.  (important because a later step will remove 'x -' from stories.)
    msgr.ulog.info("3. Persist the scrum resolved_data.  (important because a later step will remove 'x -' from stories.)")
    resolved_data = str(new_jtd_doc.scrum.head_instance_dict[new_jtd_doc.resolved_section_head])
    journaldir.write_dir_file(resolved_data + '\n', daily_o.jdir, daily_o.cday_resolved_fname)

    #     4. Write everything in old j/td back to Endeavor stories on disk, merging according to the write_item_to_story_file() call to
    msgr.ulog.info("4. Write everything in old j/td back to Endeavor stories on disk, merging according to the write_item_to_story_file() call to")
    #         insert_update_document_item(item) merge the backlog into the journal.
    # write all the tasks from the old jtd
    for story_item in old_jtd_doc.get_document_unresolved_list():
        write_item_to_story_file(story_item, user_path_o.new_task_story_file)

    #     5. Git commit the updates, which will include tasks updated to 'x -' and 'a -'.
    msgr.ulog.info("5. Git commit the updates, which will include tasks updated to 'x -' and 'a -'.")
    user_path_o.git_add_all(daily_o, f"data written to stories and resolved file from {last_journal}")

    # 6. Remove resolved items from stories using remove_item_from_story_file(r_item).
    msgr.ulog.info("6. Remove resolved items from stories using remove_item_from_story_file(r_item).")
    [remove_item_from_story_file(r_item) for r_item in resolved_items]

    # 7. Read the Endeavor stories according to load_endeavor_stories(user_path_o) (now including the old j/td tasks)
    msgr.ulog.info("7. Read the Endeavor stories according to load_endeavor_stories(user_path_o) (now including the old j/td tasks)")
    story_dir_objects: List[StoryDir] = journaldir.load_endeavor_stories(user_path_o)

    endeavor_story_docs: List[TLDocument] = [story_doc for sdo in story_dir_objects
                                             for story_doc in StoryGroup(sdo).story_docs ] #  .get_short_stories()]
    msgr.ulog.info("Load endeavor StoryDirs:...")

    # 8. Shorten the stories to max tasks in each.  Build a sprint candidate list (short backlog list)
    #    of task items from the stories.
    msgr.ulog.info("8. Shorten the stories to max tasks in each.  Build a sprint candidate list (short backlog list)")
    sprint_candidate_tasks: List[TLDocument] = list()
    for journal_story_doc in journal_story_docs:
        sprint_candidate_tasks += journal_story_doc.get_limited_tasks_from_unresolved_list() # tasks from stories in journaldir.

    for endeavor_story_doc in endeavor_story_docs:
        sprint_candidate_tasks += endeavor_story_doc.get_limited_tasks_from_unresolved_list()

    info_message = "sprint_candidate_tasks: \n" + "\n".join([str(sct) for sct in sprint_candidate_tasks])
    msgr.ulog.info(info_message)
    # 'sprint candidates': the top tasks in each story that may get into the day sprint.
    # Picking off the top 3 stories will always take from the top endeavor
    #       (if they are written in priority order)
    # however the stories within an endeavor are just in file listing order.
    # (see tlog story 'Prioritized Backlog story.txt'
    # as a work around, users can make sure only 1 story filer in each endeavor has a non zero 'maxTasks:' value.

    # msgr.ulog.info("Sprint Candidate Tasks: " + str_o_list(sprint_candidate_tasks, delimiter="\nTask::\n", prefix_delim=True))

    # 9. Pop the global sprint size number of stories off the backlog list. Add them to new j/td scrum object as t-do.
    msgr.ulog.info("9. Pop the global sprint size number of stories off the backlog list. Add them to new j/td scrum object as t-do.")
    sprint_size = TLDocument.default_scrum_to_do_task_capacity
    num_sprint_canidates = len(sprint_candidate_tasks);
    sprint_task_items = sprint_candidate_tasks[0:sprint_size]

    new_jtd_doc.add_list_items_to_scrum(sprint_task_items)

    # 10. Persist the scrum todo_data
    msgr.ulog.info("10. Persist the scrum todo_data")
    todo_tasks = new_jtd_doc.scrum.head_instance_dict[new_jtd_doc.todo_section_head]
    todo_data = str(todo_tasks)
    journaldir.write_dir_file(todo_data + '\n', daily_o.jdir, daily_o.cday_todo_fname)
    info_msg = "Sprint Items: \n"
    index = 1
    for sprint_item in todo_tasks.body_items:
        info_msg += f"{index}. {sprint_item}\n"
        index += 1
    msgr.ulog.info(info_msg)

    # 11. Git commit the updates, which will have both parts of the new scrum and the updated Endeavor stories with
    msgr.ulog.info("11. Git commit the updates, which will have both parts of the new scrum and the updated Endeavor stories with")
    user_path_o.git_add_all(daily_o, f"todo sprint written to {daily_o.cday_todo_fname}")


    msg = f"total Backlog: {num_sprint_canidates} configured sprint_size: {sprint_size} sprint  items: {len(todo_tasks.body_items)}"
    msgr.screen_log(tag, msg)
    msgr.ulog.info(tag + msg)

    # print(f"Current scrum for daily sprint:\n{new_jtd_doc.scrum}")


if __name__ == "__main__":
    main()

