#!/usr/bin/env python -d
# !/usr/local/bin/python3
"""
Composition: Top level application built of collections of TLDocument
Objects.  Stories read from Endeavor files, for example.
"""
from __future__ import annotations

import json
import os
import re
from typing import List, NamedTuple

# import mongocol
import tlconst
from endeavor import Endeavor, Story, Task
from tlconst import apCfg
from tldocument import TLDocument  # import re
import tldocument
from docsec import TLogInternalException, Item
import fileinput
from journaldir import StoryDir
import journaldir
from docsec import DocStructure
# import sys
import logging


class StoryGroup:
    """
    Adds story semantics around a group of Documents read from files in a directory
	Combines the journaldir.StoryDir and the tldocument.TLDocument to get
	a collection of tasks.
	Sets attributes in the tasks in the Documents to allow changes in the tasks to be written back to the
	    storySource: an_endeavor/story
	journal to be written back to the original stories
	"""

    story_source_attr_name = "storySource"

    def __init__(self, story_dir: StoryDir):
        self.story_dir = story_dir
        self.story_docs: List[TLDocument] = [load_and_resave_story_file_with_attribs(s_file)
                                             for s_file in self.story_dir.story_list]

    def get_endeavor_name(self):
        return os.path.basename(self.story_dir.path)

    def as_endeavor(self) -> Endeavor:
        endeavor = Endeavor(self.get_endeavor_name())
        for story_doc in self.story_docs:
            story = Story(story_doc.story_name, endeavor, story_doc.max_tasks)
            for task_item in story_doc.get_document_matching_list(tldocument.unresolved_pat):
                # todo first arg below needs to be the status.  prob implement a taskItem.get_status()
                # todo is this right for last arg?: str(taskItem.subs)
                Task(tldocument.find_status_name(task_item.get_leader()), task_item.get_title(), story,
                     task_item.detail_str())
        return endeavor

    def __str__(self):
        return "\n".join([str(d) for d in self.story_docs])


def load_and_resave_story_file_with_attribs(file_name) -> TLDocument:
    """
    Loads a file system file as a TLDocument and saves it back to disk with the following enrichment:.
        Adds 'storyName:' to the TLDocument representing a Story.
            This enable the story to be migrated to an object store.
        adds 'storySource:' 'titleHash:' to each task item in the TLDocument
            These attributes enable items to be re titled and still update the original story file.
    """
    story_doc: TLDocument = load_doc_from_file(file_name)
    story_doc.attribute_all_unresolved_items(StoryGroup.story_source_attr_name, file_name)
    story_doc.for_journal_sections_add_all_missing_item_title_hash()
    story_name = os.path.basename(file_name)
    story_name = re.sub(apCfg.story_suffix_pat, '', story_name)
    story_doc.story_name = story_name
    journaldir.write_filepath(str(story_doc), file_name)
    return story_doc


def remove_item_from_story_file(item: Item) -> Item:
    """
    Remove item from file indicated by it's 'storySource:' attribute
    always log the item being removed.
    """
    debuglog = logging.getLogger('debuglog')
    story_source = item.get_item_attrib(StoryGroup.story_source_attr_name)
    if not story_source:
        debuglog.warning(f"item to remove does not have a 'storySource:' attribute: {item.top}")
        return None
    filepath = story_source
    story_tldoc: TLDocument = load_doc_from_file(filepath)
    story_tldoc.remove_document_item(item)
    journaldir.write_filepath(str(story_tldoc), filepath)


# todo test write_item_to_story_file()
def write_item_to_story_file(item: Item, default_file=None, new_item_section_head: str = "# Added Tasks"):
    """
    Writes an item into either its original storySource, or the default if not provided.
    :param item: a task item to write.
    :param default_file: file path to write item into if there is no storySource in item
    :return: Story Document object that was written to disk
    """
    tag = "write_item_to_story_file():"
    story_source = item.get_item_attrib(StoryGroup.story_source_attr_name)
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
    story_tldoc: TLDocument = load_doc_from_file(filepath)
    story_tldoc.insert_update_document_item(item, new_item_section_head)
    journaldir.write_filepath(str(story_tldoc), filepath)
    return story_tldoc

from enum import Enum


class SearchStatus(Enum):
    # To be used with chain of responsibility like patterns
    SUCCESS = 0  # next level operation can continue
    STOP = 1     # not failed, but caller should use the message and accept intermediate result.
    FAILED = 2   # Somthing went wrong.  Consider raising an exception.


#  status: a number result code that has a name,
#  data: the path dir | a document  read and loaded with data
#  message: information to report to the user
class SearchResult(NamedTuple):
    # Supports a chain of responsibility that searches for a directory with prior data
    # then if found a different function loads it into a TLDocument .
    status: SearchStatus
    data: str | TLDocument
    message: str


def find_prev_journal_dir(latest_dir, history_months) -> SearchResult:
    file_count = 0
    dirs_to_search = history_months
    next_search_dir = latest_dir
    search_dir = latest_dir
    result = SearchResult(SearchStatus.STOP, search_dir,
                          f"No previous Journal Dir was found looking back {history_months} months.")
    while file_count == 0 and dirs_to_search > 0:
        search_dir = next_search_dir
        sfl = journaldir.get_file_names_by_pattern(
            search_dir, apCfg.story_pat)
        jfl = journaldir.get_file_names_by_pattern(
            search_dir, apCfg.blotter_pat)
        file_count = len(sfl) + len(jfl)
        if file_count > 0:
            result = SearchResult(SearchStatus.SUCCESS, search_dir,
                                  f"{len(sfl)} stories and {len(jfl)} blotters in {search_dir}")
            return result
        next_search_dir = journaldir.get_prior_dir(search_dir)  # can return None
        if not next_search_dir:
            dirs_to_search = 0  # loop to end if no sensible search_dir
        else:
            dirs_to_search -= 1
    return result


def load_doc_from_file(file_name) -> TLDocument:
    file_text = journaldir.read_file_str(file_name)
    tl_doc = TLDocument.fromtext(file_text)
    return tl_doc


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


def initialize_file_paths():
    user_path_o = journaldir.UserPaths()
    daily_o = journaldir.Daily(apCfg.convention_journal_root)
    os.makedirs(user_path_o.tmp_root, exist_ok=True)
    os.makedirs(daily_o.jrdir, exist_ok=True)
    print("Tlog Working Directory: ", os.getcwd())
    print("Tlog Temporary Directory: ", user_path_o.tmp_root)
    debuglog = logging.getLogger('debuglog')
    debuglog.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    debug_handler = logging.FileHandler(user_path_o.debug_log_file)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    debuglog.addHandler(debug_handler)
    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)
    debuglog.addHandler(info_handler)
    user_path_o.git_init_journal()
    return daily_o, debuglog, user_path_o


# todo - replace this method with 2 methods:
#    a method that builds the new blotter with a scrum that has all the previously resolved 'x - '
def write_resolved_tasks(daily_o: Daily, old_jtd_doc: object) -> object:
    """
    Get a new blotter doc started, with '/ -' and also write them as 'u - ' to the resolved file.
    Include 'x -' and 'a -' in the new blotter for next steps in main()
    """
    #         c. 
    #     3. Persist the scrum resolved_data.  (important because a later step will remove 'x -' from stories.)

    # reads the current resolved into a doc if there are any. 
    resolved_doc: TLDocument = load_doc_from_file(journaldir.path_join(daily_o.jrdir, daily_o.cday_resolved_fname))
    
    # loads them into a blotter doc scrum object as resolved.
    new_blotter_doc: TLDocument = TLDocument()
    new_blotter_doc.add_section_list_items_to_scrum(
        resolved_doc.journal)  # items in resolved file from earlier today run of tlog
 
    # gets a list of the in '/ -' in-progress from old blotter 
    in_progress_items = old_jtd_doc.select_all_section_items_by_pattern(
        tldocument.statuses.in_progress.pattern)  # items in old blotter that are in progress
    
    # makes a copy of the list and modifies the leader from '/ - ' to 'u - ' for the resolved doc
    # unfinished_item_copies = [item.deep_copy(tldocument.top_parser_pat) for item in in_progress_items]
    # for item in unfinished_item_copies:
    #     # toggle in progress to unfinished
    #     item.modify_item_top(tldocument.statuses.in_progress.pattern, tldocument.unfinished_s)
    
    # extract 'x -' completed tasks from old blotter.  Add them to new blotter scrum object as resolved
    # new_blotter_doc.add_list_items_to_scrum(unfinished_item_copies)
    xa_resolved_items = old_jtd_doc.select_all_section_items_by_pattern(
        tldocument.resolved_pat)  # items in jtd that are resolved (xa)
    new_blotter_doc.add_list_items_to_scrum(xa_resolved_items) # puts xa_resolved_items in the resolved Section
    [remove_item_from_story_file(r_item) for r_item in xa_resolved_items]

    resolved_data = str(new_blotter_doc.scrum.head_instance_dict[new_blotter_doc.resolved_section_head])
    print("resolved_data:", resolved_data)
    journaldir.write_dir_file(resolved_data + '\n', daily_o.jrdir, daily_o.cday_resolved_fname)

    # Forces unfinished work from current blotter file directly into the new scrum.
    new_blotter_doc.add_list_items_to_scrum(in_progress_items)  # puts in_progress_items in the to do Section
    # This feature can look like a bug because the item might be violating curent priority
    # to obey priority, user can simply toggle the item from '/ - ' to 'd - '.

    return new_blotter_doc


def update_endeavors(daily_o, last_journal_message_string, old_blotter_doc, resolved_items, user_path_o):
    for story_item in old_blotter_doc.get_document_matching_list(tldocument.unresolved_pat):
        write_item_to_story_file(story_item, user_path_o.new_task_story_file)
    for story_item in old_blotter_doc.get_document_matching_list(tldocument.scheduled_pat):
        write_item_to_story_file(story_item, user_path_o.new_task_story_file)
    user_path_o.git_add_all(daily_o, f"data written to stories and resolved file from {last_journal_message_string}")
    # [remove_item_from_story_file(r_item) for r_item in resolved_items]


def load_task_data(daily_o, user_path_o)-> SearchResult:
    old_blotter_doc = TLDocument(day=daily_o.domth)

    os.makedirs(daily_o.j_month_dir, exist_ok=True)  # make the dir for the current jounal file
    os.makedirs(user_path_o.old_journal_dir, exist_ok=True)  # dir for saving off old journal
    os.makedirs(os.path.join(user_path_o.endeavor_path, apCfg.default_endeavor_name),
                exist_ok=True)  # dir default an_endeavor
    # look back in history to find past journal dir
    find_prev_result = find_prev_journal_dir(daily_o.j_month_dir, tlconst.apCfg.look_back_months)
    status, prev_journal_dir, message = find_prev_result
    if status == SearchStatus.SUCCESS:
        story_dir_o = StoryDir(prev_journal_dir)
        j_file_list = journaldir.get_file_names_by_pattern(
            story_dir_o.path, apCfg.blotter_pat)  # blotter {date].md files

        # load the latest blotter into the blotter for today
        last_blotter = "no_blotter_yet"
        if len(j_file_list) > 0:
            last_blotter = j_file_list[-1]
            old_blotter_doc.add_lines(fileinput.input(last_blotter))
        return SearchResult(SearchStatus.SUCCESS, old_blotter_doc, f"The last blotter was: {last_blotter}" )
    else:
        return find_prev_result



def main():
    """
    Requires no command line arguments, but may use them to interpret the user environment differently.
    User environment includes directories of story files with tasks, which will be read into lists of stories.
        See Tlog User Documentation.md

    # ==== process_work done
    #     1. Load the "old" blotter file.
    #     2. make_scrum_resolved() as:
    #         a. start with the existing resolved file add to new blotter doc scrum object as resolved.
    #         b. extract '/ -' in-progress from old blotter.  Flip them to 'u -'. add them to new blotter scrum
    #         object as resolved.
    #         c. extract 'x -' completed tasks from old blotter.  Add them to new blotter scrum object as resolved
    #     3. Persist the scrum resolved_data.  (important because a later step will remove 'x -' from stories.)

    #     4. Write everything in old blotter back to Endeavor stories on disk, merging according to the write_
    #     item_to_story_file() call to
    #     5. Git commit the updates, which will include tasks updated to 'x -' and 'a -'.
    #     6. Remove resolved items from stories using remove_item_from_story_file(r_item).

    #     7. Read the Endeavor stories according to load_endeavor_stories(user_path_o)
    #     (now including the old blotter tasks)

    # ==== plan_day
    #     8.a Shorten the stories to max tasks in each.  Build a sprint candidate list (short backlog list)
    #     of task items from the stories.
    #     8.b Get scheduled tasks from endeavor story docs.  Build a list of scheduled tasks.
    #     9. Pop the global sprint size number of stories off the backlog list. Add em to new blotter scrum object as to do.
    #     10. Move existing blotter files out of the journaldir
    #     11. Persist the scrum td and sched
    #     12. Git commit the updates, which will have both parts of the new scrum and the updated Endeavor stories with
    """

    # initialize everything
    daily_o, debuglog, user_path_o = initialize_file_paths()

    # ############################
    # Gather input state from Disk and command line
    # ============================
    #     1. Load the "old" blotter file.
    task_load_result: SearchResult = load_task_data(daily_o, user_path_o)

    #     2. Get a new blotter doc started, with '/ -' and also write them as 'u - ' to the resolved file.
    #         still need the 'x -' and 'a -' to clear them out of the source Endeavors stories.
    #         a. start with the existing resolved file add to new blotter doc scrum object as resolved.
    #         b. extract '/ -' in-progress from old blotter.  Flip them to 'u -'. add them to new blotter scrum
    #         object as resolved.
    #         c. extract 'x -' completed tasks from old blotter.  Add them to new blotter scrum object as resolved
    #     3. Persist the scrum resolved_data.  (important because a later step will remove 'x -' from stories.)
    new_blotter_doc: TLDocument
    if task_load_result.status == SearchStatus.SUCCESS:
        assert isinstance(task_load_result.data, tldocument.TLDocument), \
            "Prior task contents should have been loaded into a tldocument.TLDocument"
        old_blotter_doc = task_load_result.data
        new_blotter_doc = write_resolved_tasks(daily_o, old_blotter_doc)
        resolved_items = new_blotter_doc.scrum.head_instance_dict[new_blotter_doc.resolved_section_head].body_items

        #     4. Write everything in old blotter back to Endeavor stories on disk, merging according to the
        #           write_item_to_story_file() doc string.
        #     5. Git commit the updates, which will include tasks updated to 'x -' and 'a -'.
        #     6. Remove resolved items from stories using remove_item_from_story_file(r_item).
        update_endeavors(daily_o, task_load_result.message, old_blotter_doc, resolved_items, user_path_o)
    else:
        print(task_load_result.message)
        new_blotter_doc = TLDocument()
    #     7. Read the Endeavor stories according to load_endeavor_stories(user_path_o)
    #     (now including the old blotter tasks)
    story_dir_objects: List[StoryDir] = journaldir.load_endeavor_stories(user_path_o)

    all_endeavor_story_groups: List[StoryGroup] = [StoryGroup(sdo) for sdo in story_dir_objects]

    story_docs_from_all_endeavors: List[TLDocument] = []
    endeavor_models: List[Endeavor] = []

    for esg in all_endeavor_story_groups:
        story_docs_from_all_endeavors += esg.story_docs
        endeavor_models.append(esg.as_endeavor())

    # 7.a load / upsert the Endeavors to Mongo.
    # for endeavor in endeavor_models:
    #     mongocol.upsert_endeavor(endeavor)
    #
    # mongocol.list_endeavors()

    #     8.a Shorten the stories to max tasks in each.  Build a sprint candidate list (short backlog list)
    #     of task items from the stories.
    sprint_candidate_tasks: List[Item] = list()
    for endeavor_story_doc in story_docs_from_all_endeavors:
        sprint_candidate_tasks += endeavor_story_doc.get_limited_tasks_from_unresolved_list()

    debug_message = "sprint_candidate_tasks: \n" + "\n".join([str(sct) for sct in sprint_candidate_tasks])
    debuglog.debug(debug_message)
    # 'sprint candidates': the top tasks in each story that may get into the day sprint.
    # Picking off the top 3 stories will always take from the top an_endeavor
    # Stories within the Endeavor are prioritized according to prioritized.md in the an_endeavor dir.

    #   8.b Get scheduled tasks from endeavor story docs.  Build a list of scheduled tasks.
    scheduled_tasks: List[Item] = list()
    for endeavor_story_doc in story_docs_from_all_endeavors:
        scheduled_tasks += endeavor_story_doc.get_document_matching_list(tldocument.scheduled_pat)

    # 9. Pop the global sprint size number of stories off the backlog list. Add em to new blotter scrum object as to do.
    sprint_size = TLDocument.default_scrum_to_do_task_capacity
    num_sprint_candidates = len(sprint_candidate_tasks);
    sprint_task_items: List[Item] = list()
    sprint_task_items += sprint_candidate_tasks[0:sprint_size]

    new_blotter_doc.add_list_items_to_scrum(sprint_task_items)
    new_blotter_doc.add_list_items_to_scrum(scheduled_tasks)    # the scrum object knows the section
                                                                # to put these in based on the leader pattern

    # 10. Move existing blotter files out of the journaldir
    blotter_file_list = journaldir.get_file_names_by_pattern(daily_o.j_month_dir, apCfg.blotter_pat)
    if len(blotter_file_list) > 0:
        journaldir.move_files(user_path_o.old_journal_dir, blotter_file_list)

    # 11. Persist the scrum td and sched
    # todo new_scrum is just a reference to new_blotter_doc.scrum.   I doubt that is what I mean to do.
    new_scrum: DocStructure = new_blotter_doc.scrum
    blotter_data: str = new_scrum.get_report_str([new_blotter_doc.blotter_section_head,
                                                  new_blotter_doc.scheduled_section_head])
    journaldir.write_dir_file(blotter_data + '\n', daily_o.j_month_dir, daily_o.cday_blotter_fname)
    blotter_tasks = new_blotter_doc.scrum.head_instance_dict[new_blotter_doc.blotter_section_head]

    debug_msg = "Sprint Items: \n"
    index = 1
    for sprint_item in blotter_tasks.get_body_data():
        debug_msg += f"{index}. {sprint_item}\n"
        index += 1
    debuglog.debug(debug_msg)

    # 12. Git commit the updates, which will have both parts of the new scrum and the updated Endeavor stories with
    user_path_o.git_add_all(daily_o, f"task blotter sprint written to {daily_o.cday_blotter_fname}")

    msg1 = f"total Backlog: {num_sprint_candidates} configured sprint_size: {sprint_size} sprint items: "
    msg1 += f"{len(blotter_tasks.get_body_data())}"
    msg2 = f"The task blotter file is: {daily_o.cday_blotter_fname}"
    debuglog.debug(msg1)
    debuglog.debug(msg2)
    print(msg1)
    print(msg2)


if __name__ == "__main__":
    main()
