#!/usr/local/bin/python3
"""
Composition: TLDocument class contains the tlog application semantics purpose
for Section objects and the text parsing patterns for Sections and Items along
with the semantic significance of those patterns


See tldocument.py for pattern_strs that classify input
lines

Logic for building TLDocuments line by line from text: (needs update)
    There is always a current Section in a Document.
    There is always a current Item in a Section.

    If data is a section header,
    and
        if the current section is empty, use it
        else make a new current section with the data.
    If data is an item header other than 'do',
        add it to the current section.
        adding an item to a Section will:
            if the current item is empty, use it.
            else make a new current Item with the data.
            return a new current_item
    else if data is a 'do' item header
        add it to the backlog Section
    else

"""

import re
from collections import namedtuple
from typing import List, Dict, Pattern

from docsec import Section, DocStructure, Item

blank_ln_pat = re.compile("^\s*$")

"""
TLDocument
    journal - list of Section objects created from text lines that the caller reads and writes to or from a file 
                - currently (2020-12) 'd -' items are not included in the journal,
    backlog - special section intended to represent 'sprint candidate' work that may go into the scrum 'todo'.
                - currently (2020-12) 'd -' items are added to the backlog section, not the journal sections
    scrum   - a DocStructure object with 
                - a section for Resolved tasks. (heading '# Resolved {day of month}' ) 
                - a Section with a limited number of tasks for current work session (heading '# To Do {day of month}')
"""
default_max_stories = 3 # todo add support for this in tlog.py.
                        #   At present tlog does not have any object representing an an_endeavor.
                        #   Add that first, then read maxStories of the Endeavor line in endeavors.md
                        #   an_endeavor.Endeavor already supports max stories using this default.
default_maxTasks = 1  # used if not specified in a story.txt



# -------- Status configuration
# -------- The next several lines establish the ability to parse tasks to find the status name from a regex that
# -------- matches a leader on a Task Item. The pattern passed to docsec.Item() is built here based on the
# -------- statuses configured in fill_status_dict()
# -------- Although docsec.Item().get_leader() based on top_parser_pat defined here, it is find_status_name(leader_str)
# -------- that can interpret the leader to get a status name.
# --------

# Define the Status type fields.
Status = namedtuple('Status', ['name', 'val', 'pat_str', 'pattern'])

def add_status(sd: Dict[str, Status], name, val, pat_str):
    """
    Creates a side affect of updating te dict sd with a Status created using athe arges configured in
    fill_status_dict().   This function also compiles a pattern to store in the Status object
    """
    sd[name] = Status(name, val, pat_str, re.compile(pat_str))

def print_statuses(sd: Dict[str, Status]):
    for status_key in sd.keys():
        print(f"name:{sd[status_key].name} val:{sd[status_key].val} pat_str:{sd[status_key].pat_str} ", end='')
        print(f"pattern:{sd[status_key].pattern} type(pattern): {type(sd[status_key].pattern)}" )

def fill_status_dict(sd):
    """
    The supported statuses for tasks are configured here with a name, a value, a pattern string.
    add_status() is called for each configured status to load the sd dictionary
    """
    for status_record in [
                            # name, val, pat_str, pattern
                            ('abandoned', 'a', "^[aA] *-"),
                            ('completed', 'x', "^[xX] *-"),
                            ('scheduled', 's', "^[sS] *-"),
                            ('in_progress', '/', r'^[/\\] *-'),  # used here in head_str and not_do_str
                            ('unfinished', 'u', "^[uU] *-"),
                            ('do', 'd', "^[dD] *-") # Good usage in Document to configure the scrum Docstruct
                                                    # used here as part of head_str
                                                    # Good usages in TLDocument to make scrum and add_line()
                        ]:
        add_status(sd, *status_record)

status_dict: Dict[str, Status] = {}
fill_status_dict(status_dict)

# to build statuses of type StatusStruct with dot access to the field names 'abandoned', 'completed', etc.
# where the field names get a Status named tuple.
task_status_vals = [status_dict[status_key].val for status_key in status_dict.keys()]
task_status_names = [status_dict[status_key].name for status_key in status_dict.keys()]
task_status_objects = [status_dict[status_key] for status_key in status_dict.keys()]
StatusStruct = namedtuple('StatusStruct', task_status_names)
statuses = StatusStruct(*task_status_objects)

resolved_str = "|".join([statuses.completed.pat_str, statuses.abandoned.pat_str])
resolved_pat = re.compile(resolved_str)  # Used externally in in TLDocument get_xa ..

unfinished_s = "u -"  # used in Item in modify_item_top() that i am refactoring
                        # todo re-code with dash to enable status_dict to be used.

head_str = "|".join(
    [resolved_str, statuses.scheduled.pat_str, statuses.in_progress.pat_str, statuses.do.pat_str, statuses.unfinished.pat_str])  # used here in head_pat and leader_group_str
head_pat = re.compile(head_str)


not_do_str = "|".join([resolved_str, statuses.in_progress.pat_str, statuses.unfinished.pat_str])  # just used here
not_do_pat = re.compile(not_do_str)  # only used in Document

unresolved_str = "|".join([statuses.in_progress.pat_str, statuses.do.pat_str, ])
    # used to write old data back to endeavors
    # used to get sprint candidates
unresolved_pat: Pattern = re.compile(unresolved_str)

scheduled_pat: Pattern = re.compile(statuses.scheduled.pat_str)

leader_group_str = "(" + head_str + ")"  # only used here
title_group_str = r"\s*(.*\S)\s*$"  # only used here

# this pattern used 2 regex match groups to parse lines as task Items
# composed of a leader at the beginning of the line, and some text as the title.
top_parser_pat = re.compile(leader_group_str + title_group_str)


def find_status_name(leader_str):
    for task_status_object in task_status_objects:
        # print(f"{task_status_object}")
        if task_status_object.pattern.match(leader_str):
            # print(f"{leader_str} matches {task_status_object.name} ({task_status_object.val})")
            return task_status_object.name
    return None

# --------


class TLDocument:
    """
    Document objects are made from lists of text lines to be made into Sections
    and Items.

    Methods are included to support collecting items by pattern for the caller
    to build the scrum object.

    Any line beginning with d, D, s, S, x, X, a, A,  /, \ is a task line.
        d, D - represent 'do' tasks, and get added to the document.backlog
        s, S - represent 'scheduled' tasks for later.  Ignored for prioritzation today.
        x, x - represent complete tasks and get added to the scrum document to write as resolved.
        a, A - represent abanndon tasks, no longer needed and get added to the scrum document to write as resolved.
        /, \ - represent in progress tasks,  with a copy changed to
                u - (unfinished) and added to the scrum document and written as resolved section.
    If a task line is followed by lines that are a bullet list, or free text,
    the additional lines will be kept together as part of the task Item object.

    Any input text line that is not a Section or Item header gets added to the
    current Item.

    Items that begin a section, sometimes do not have a task line

    Attributes are supported using the class TLAttribute

    Some attributes are supported as properties in the Document class and
    implemented as Attributes on a special first section:
        doc_name DocName: (read / write) for file system document name
        max_tasks max_tasks: (read / write)
        story_name storyName: (read / write) for name used in other task stores

    The Section and Item classes can be injected with attributes, but
    they should be optional in most or all cases.

    The class TLDocument holds the semantic meaning for the
    documents needed by tlog.

    The 'journal' has evolved to be created of Sections and Items *as read from disk*.
    The name 'journal' is being replaced with 'blotter', as the active file where work and status changes are made.

    The class DocStructure implements the scrum object to associate Item leader types
    with semantically meaningful special sections like '# Resolved' and '# To Do', and '# Scheduled for later'
    """

    default_scrum_to_do_task_capacity = 5  # default number of backlog tasks to take into a day sprint

    defaut_in_prog_head = "#In progress"
    doc_name_attr_str = "DocName"

    # need a constructor that takes a list of lines
    # todo - need tests for this
    def __init__(self, name=None, input_lines=None, day=None,
                 initial_task_capacity=default_scrum_to_do_task_capacity):
        """
        Public interface Instance attributes:
            journal - the Sections and Items collected in past days
            in_progress - List of in progress Items to be put in the current day
                document.
            backlog - Section containing 'do' Items.

        """
        domth: str = day if day else ""
        self.todo_section_head = f'# To Do {domth}'
        self.resolved_section_head = f'# Resolved {domth}'
        self.scheduled_section_head = f'# Scheduled {domth}'
        self.scrum = DocStructure(Section.head_pat, top_parser_pat) # see doc for make_scrum()
        self.scrum.add_leader_entry(self.resolved_section_head, [statuses.abandoned.pattern,
                                                                 statuses.completed.pattern])
        self.scrum.add_leader_entry(self.todo_section_head, [statuses.in_progress.pattern,
                                                             statuses.do.pattern])
        self.scrum.add_leader_entry(self.scheduled_section_head, [statuses.scheduled.pattern])

        self._doc_name = name or ""
        self.task_capacity = initial_task_capacity
        self.initialize_journal()
        self.add_lines(input_lines)

    def initialize_journal(self):
        """
        Initializes the journal list of sections to make sure there is a section at journal[0]
        and a current section
        """
        self.journal = []
        # self.in_progress = Section(top_parser_pat, None)  # external logic sets to today
        # self.backlog = Section(TLDocument.top_parser_pat)
        self.add_section_from_line(None)

    # --- story_name property
    story_name_attr_str = 'storyName'

    def _get_story_name(self):
        "getter for story_name"
        return self.get_doc_attrib(TLDocument.story_name_attr_str)

    def _set_story_name(self, name):
        "setter for story_name"
        self.set_doc_attrib(TLDocument.story_name_attr_str, name)

    story_name = property(_get_story_name, _set_story_name)

    #--- doc_name property
    doc_name_attr_str = "DocName"

    def _get_doc_name(self):
        "getter for doc_name"
        return self.get_doc_attrib(TLDocument.doc_name_attr_str)

    def _set_doc_name(self, name):
        "setter for doc_name"
        self.set_doc_attrib(TLDocument.doc_name_attr_str, name)

    doc_name = property(_get_doc_name, _set_doc_name)

    #--- max_tasks property
    max_tasks_attr_str = "maxTasks"

    def _get_max_tasks(self):
        "getter for max_tasks"
        return self.get_doc_attrib(TLDocument.max_tasks_attr_str)

    def _set_max_tasks(self, max):
        "setter for doc_name"
        self.set_doc_attrib(TLDocument.max_tasks_attr_str, max)

    max_tasks = property(_get_max_tasks, _set_max_tasks)

    # todo - need tests for this
    """
    """
    def add_lines(self, r_lines):
        """
        make sections, which contain items:
            First, read and classify each input line as one or more of:
             - a mark down heading for a new Section
             - a task line to create a new Item to add to the list under the
               current Section
             - text to put under the current Item

            self
            r_lines	raw lines
        """
        prev_line_blank = False

        if not r_lines:
            return

        for line in r_lines:
            if blank_ln_pat.match(line):
                if prev_line_blank:
                    continue
                prev_line_blank = True
            else:
                prev_line_blank = False

            data = line.rstrip("\n")
            # print("add_lines data:" + data)
            self.add_document_line(data)
            # self.add_line_deprecated(data)

    def add_document_line(self, data):
        """
        Add a single data line into the document according to
        pattern_strs in the Item and Section classes.
        The TLDocument journal will be structured with Sections and Items matching the input text
        (This is a change from a deprecated approach, which separated out 'd -' items to a backlog.
        The backlog will be built when needed as a simple sequenced list of items.)
        """
        if data is None:
            return
        if Section.head_pat.match(data):
            if self.current_section.is_empty():
                # Putting a header on initial section
                self.current_section.add_section_line(data)
                self.last_add = self.current_section
            else:
                # New section.
                self.add_section_from_line(data)

        elif top_parser_pat.match(data):
            self.current_section.add_section_line(data)
            self.last_add = self.current_section
        else:
            self.last_add.add_section_line(data)



    def add_section_from_line(self, data: object) -> object:
        """

        :param data: string to create a section
        :return:
        """
        self.current_section = Section(top_parser_pat, data)
        self.journal.append(self.current_section)
        self.last_add = self.current_section
        return self.current_section

    @classmethod
    def fromtext(cls, text):
        """create a Document from multiline text parameter"""
        new_document = TLDocument()
        if not text:
            return new_document
        lines = text.split("\n")
        new_document.add_lines(lines)
        return new_document

    # todo test this.
    def get_doc_attrib(self, key):
        """
        Return the Document attribute matching key, or None.
        The Document attributes are the attributes of the first Section (index 0)
        on the journal, only if that Section has no text in its 'header' member
        """
        if len(self.journal[0].header) == 0:
            return self.journal[0].get_section_attrib(key)
        else:
            return None

    def set_doc_attrib(self, akey, aval):
        "Set Document attributes by putting them in an otherwise empty first Section in the journal"
        if self.journal[0].is_attrib_section():
            # Document set_doc_attrib calling Section Set Attrib
            self.journal[0].set_sec_attrib(akey, aval)
        else:
            s = Section(top_parser_pat)
            s.set_sec_attrib(akey, aval)
            self.journal.insert(0, s)

    def journal_str(self):
        "Return the journal as text lines"
        s = ""
        for section in self.journal:
            sec_str = str(section)
            sec_newline = "\n" if s and sec_str else ""
            s += sec_newline + sec_str
        return s

    # def in_progress_str(self):
    #     "Return the in_progress section as a string."
    #     return str(self.in_progress)


    def get_limited_tasks_from_unresolved_list(self, )-> List[Item]:
        mt = default_maxTasks
        if self.max_tasks:
            mt: int = int(self.max_tasks)

        limited_list: List[Item] = self.get_document_matching_list(unresolved_pat)[0:mt]
        return limited_list

    def get_document_items_by_pattern(self, match_pat: Pattern):
        matched_items: List[Item] = list()
        section: Section
        for section in self.journal:
            matched_items += section.get_matching_items(match_pat)
        return matched_items

    def get_document_matching_list(self, pattern: re.Pattern) -> List[Item]:
        """
        Caller will be responsible for slicing to max_tasks if needed.
        :return all tasks from all section matching TLDocument.unresolved_pat
        """
        matching_items: List[Item] = list()
        section: Section
        for section in self.journal:
            matching_items += section.get_matching_items(pattern)
        return matching_items

    def attribute_all_unresolved_items(self, key, val):
        """creates attribute on every item in the backlog section.
        Useful for putting the storySource attribute on all the items read out of a story.
        :param :key the name of the attribute to set.
        param :val the value to set for the attribute.
        """
        for item in self.get_document_matching_list(unresolved_pat):
            item.set_attrib(key, val)

    def for_journal_sections_add_all_missing_item_title_hash(self):
        """
        See Section method add_all_missing_item_title_hash(self) and Item method add_missing_title_hash(self)
        :return: None
        """
        for section in self.journal:
            section.add_all_missing_item_title_hash()


    def shorten_task_list(self, task_list: List, num_tasks=None):
        """discard tasks in the task_list beyond num_tasks
        If max_tasks is set and num_tasks is not provided,
        use max_tasks as the number of tasks to keep.
        If neither is provided, keep all tasks.
        """
        max_t = self.max_tasks or len(self.backlog.body_items)
        num_t = num_tasks or max_t
        num_t = int(num_t)
        return list(task_list[0:num_t])

    # def shorten_in_progress(self, num_tasks=None):
    #     """
    #     discard extra tasks in the in_progress section
    #     """
    #     self.in_progress.body_items = self.shorten_task_list(
    #         self.in_progress.body_items, num_tasks)
    #     return self


    def __str__(self):
        s = self.journal_str() # + "\n"
        # s += self.in_progress_str() + "\n" if not self.in_progress.is_empty() else ""
        # s += self.backlog_str()
        return s


    def add_section_list_items_to_scrum(self, section_list: List[Section]):
        """Given list of Section objects, add all their Items to the scrum"""
        for section in section_list:
            self.add_section_items_to_scrum(section)

    def add_section_items_to_scrum(self, section: Section):
        """Given a single Section object, add all it's Items to the scrum"""
        self.add_list_items_to_scrum(section.body_items)

    def add_list_items_to_scrum(self, item_list: List[Item]):
        """Given a list of Item objects, add them all to the scrum"""
        for item in item_list:
            self.scrum.insert_item(item)

    def select_all_section_items_by_pattern(self, pattern) -> List[Item]:
        all_items: List[Item] = list()
        for section in self.journal:
            all_items += section.get_matching_items(pattern)
        return all_items


    def remove_document_item(self, item: Item):
        """
        Search all Sections in the Journal list and the backlog Section for an Item according
        to the Section.find_item() criteria.
            if a match is found, remove it
        assume only 1 removal is required because items should not be duplicated in a TLDocument
        return: self
        """
        section: Section
        for section in self.journal:
            if section.find_item(item):
                section.remove_item(item)
        # self.backlog.remove_item(item)
        return self


    def insert_update_document_item(self, item, default_section_heading="# New items"):
        """
        Search all Sections in the Journal list and the backlog Section for an Item according
        to the Section.find_item() criteria.
            if a match is found, replace the matched Item with item.
        return: self
        """
        matching_item = None
        section: Section
        for section in self.journal:
            matching_item = section.find_item(item) #.find_replace_item_by_titleHash(item)
            if matching_item:
                break
        if matching_item:
            matching_item.merge_parts(item) # item reference in the current section iteration from above loop.
        else:
            self.insert_new_item_into_journal_section(default_section_heading, item)
        return self

    def insert_new_item_into_journal_section(self, section_heading: str, item: Item):
        """
        add item into the journal section matching section_heading.
        Create a matching the section if necessary.
        """
        added_item: bool = False
        for section in self.journal:
            if section.header == section_heading:
                section.add_item(item, head_insert=True) # todo, make head_insert behavior part of the Section creation
                added_item = True
        if not added_item:
            new_section: Section = self.add_section_from_line(section_heading)
            new_section.add_item(item, head_insert=True) # todo, make head_insert behavior part of the Section
                                                         #   creation pass in head_insert=true


def debExit(message=""):
    "This func just gets temporarily inserted for top down re checking of main()"
    print("EARLY DEBUG exit(): " + message)
    exit()


def main():
    print("Model classes for tlog.py")


if __name__ == '__main__':
    main()
