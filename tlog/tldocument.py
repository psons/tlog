#!/usr/local/bin/python3
"""
Composition: TLDocument class contains the tlog application semantics purpose
for Section objects and the text parsing patterns for Sections and Items along
with the semantic significance of those patterns


See tldocument.py for pattern_strs that classify input
lines

Logic for building TLDocuments from text: (needs update)
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
from typing import List

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

class TLDocument:
    """
    Document objects are made from lists of text lines to be made into Sections
    and Items.

    Methods are included to support collecting items by pattern for the caller
    to build the scrum object.

    Any line beginning with d, D, x, X,  /, \ is a task line.
        d, D - represent 'do' tasks, and get added to the document.backlog
        x, x - represent complete tasks and get added to the current Section
        /, \ - represent in progress tasks,  with a copy changed to
                u - (unfinished) and added to the scrum object Resolved section.
    If a task line is followed by lines that are a bullet list, or free text,
    the additional lines will be kept together as part of the task Item object.

    Any input text line line that is not a Section or Item header gets added to the
    current Item.

    Items that begin a section, sometimes do not have a task line

    Support multiline task Items.

    Attributes are supported using the class TLAttribute

    Some attributes are supported as properties in the Document class and
    implemented as Attributes on a special first section:
        doc_name DocName: (read / write)
        max_tasks maxTasks: (read / write)

    The Section and Item classes can be injected with attributes, but
    they should be optional in most or all cases.

    ## Evolution:
    The class TLDocument is refactored over time to hold any semantic meaning for the
    documents needed by tlog.

    The 'journal' has evolved to be created of Sections and Items *as read from disk*.
    The name journal may not make sense anymore, and this could be a list
    named document_sections in a generic Document class free of TLog semantics,
    possibly just being a Markdown Document.

    The class DocStructure implements the scrum object to associate Item leader types
    with semantically meaningful special sections like '# Resolved' and '# To Do'.
    """
    default_maxTasks = 1 # used if not specified in a story.txt
    default_scrum_to_do_task_capacity = 5  # default number of backlog tasks to take into a day sprint

    defautInProgHead = "#In progress"
    dname_attr_str = "DocName"

    # Item and leader related settings:
    abandoned_str = "^[aA] *-"
    abandoned_pat = re.compile(abandoned_str)
    completed_str = "^[xX] *-"
    completed_pat = re.compile(completed_str)
    resolved_str = "|".join([completed_str, abandoned_str])
    resolved_pat = re.compile(resolved_str)  # Used externally in in TLDocument get_xa ..

    in_progress_str = r'^[/\\] *-' # used here in head_str and not_do_str
    in_progress_pat = re.compile(in_progress_str) # used in Item in modify_item_top() that i am refactoring

    unfinished_s = "u -"  # used in Item in modify_item_top() that i am refactoring
    unfinished_str = "^[uU] *-"
    unfinished_pat = re.compile(unfinished_str)  # used in test for Item in modify_item_top() that i am refactoring
                                                # Good usage in Document to configures the scrum Docstruct
    do_str = "^[dD] *-"  # used here as part of head_str
    do_pat = re.compile(do_str)  # Good usages in TLDocument to make scrum and add_line()

    head_str = "|".join([resolved_str, in_progress_str, do_str, unfinished_str])  # used here in head_pat and leader_group_str
    head_pat = re.compile(head_str)

    not_do_str = "|".join([resolved_str, in_progress_str, unfinished_str])  # just used here
    not_do_pat = re.compile(not_do_str)  # only used in Document

    unresolved_str = "|".join([in_progress_str, do_str])  # used to get sprint candidates from the doc
    unresolved_pat = re.compile(unresolved_str)

    leader_group_str = "(" + head_str + ")" # only used here
    title_group_str = r"\s*(.*\S)\s*$"  # only used here
    # top_parser_str = leader_group_str + title_group_str
    top_parser_pat = re.compile(leader_group_str + title_group_str)

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
        self.scrum = DocStructure(Section.head_pat, TLDocument.top_parser_pat) # see doc for make_scrum()
        self.scrum.add_leader_entry(self.resolved_section_head, [TLDocument.abandoned_pat,
                                                                 TLDocument.completed_pat, TLDocument.unfinished_pat])
        self.scrum.add_leader_entry(self.todo_section_head, [TLDocument.in_progress_pat, TLDocument.do_pat])

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
        self.in_progress = Section(TLDocument.top_parser_pat, None)  # external logic sets to today
        # self.backlog = Section(TLDocument.top_parser_pat)
        self.add_section_from_line(None)

    def _get_doc_name(self):
        "getter for doc_name"
        return self.get_doc_attrib(TLDocument.dname_attr_str)

    def _set_doc_name(self, name):
        "setter for doc_name"
        self.set_doc_attrib(TLDocument.dname_attr_str, name)

    doc_name = property(_get_doc_name, _set_doc_name)

    max_tasks_attr_str = "maxTasks"

    def _get_max_tasks(self):
        "getter for maxTasks"
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

        elif TLDocument.top_parser_pat.match(data):
            self.current_section.add_section_line(data)
            self.last_add = self.current_section
        else:
            self.last_add.add_section_line(data)


    def add_line_deprecated(self, data):
        """
        Add a single data line into the document according to
        pattern_strs in the Item and Section classes.
        """
        if data is None:
            return
        # todo
        #  do items are going into the backlog section, not the latest journal section.
        #  change that to put them into journal sections ny line, and can extract a backlog later by whole items.
        if TLDocument.do_pat.match(data):
            self.backlog.add_section_line(data)
            self.last_add = self.backlog


        elif Section.head_pat.match(data):
            if self.current_section.is_empty():
                # Putting a header on initial section
                self.current_section.add_section_line(data)
                self.last_add = self.current_section
            else:
                # New section.
                self.add_section_from_line(data)

        elif TLDocument.not_do_pat.match(data):
            self.current_section.add_section_line(data)
            self.last_add = self.current_section
        else:
            self.last_add.add_section_line(data)

    def add_section_from_line(self, data: object) -> object:
        """

        :param data: string to create a section
        :return:
        """
        self.current_section = Section(TLDocument.top_parser_pat, data)
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
            s = Section(TLDocument.top_parser_pat)
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

    def in_progress_str(self):
        "Return the in_progress section as a string."
        return str(self.in_progress)


    def get_limited_tasks_from_unresolved_list(self, )-> List[Item]:
        mt = TLDocument.default_maxTasks
        if self.max_tasks:
            mt: int = int(self.max_tasks)

        limited_list: List[Item] = self.get_document_unresolved_list()[0:mt]
        return limited_list


    def get_document_unresolved_list(self) -> List[Item]:
        """
        Caller will be responsible for slicing to maxTasks if needed.
        :return all tasks from all section matching TLDocument.unresolved_pat
        """
        unresolved_items: List[Item] = list()
        section: Section
        for section in self.journal:
            unresolved_items += section.get_matching_items(TLDocument.unresolved_pat)
        return unresolved_items


    def attribute_all_unresolved_items(self, key, val):
        """creates attribute on every item in the backlog section.
        Useful for putting the storySource attribute on all the items read out of a story.
        :param :key the name of the attribute to set.
        param :val the value to set for the attribute.
        """
        for item in self.get_document_unresolved_list(): # .backlog.body_items:
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

    def shorten_in_progress(self, num_tasks=None):
        """
        discard extra tasks in the in_progress section
        """
        self.in_progress.body_items = self.shorten_task_list(
            self.in_progress.body_items, num_tasks)
        return self


    def __str__(self):
        s = self.journal_str() # + "\n"
        # s += self.in_progress_str() + "\n" if not self.in_progress.is_empty() else ""
        # s += self.backlog_str()
        return s


    def add_section_list_items_to_scrum(self, section_list: List[Section]):
        """Given list of Section objects, add all it's Items to the scrum"""
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
        #todo add a section to contain the new item. or use an already existing '# New' section. needed by insert_update_document_item
        added_item: bool = False
        for section in self.journal:
            if section.header == section_heading:
                section.add_item(item)
                added_item = True
        if not added_item:
            new_section: Section = self.add_section_from_line(section_heading)
            new_section.add_item(item)


def debExit(message=""):
    "This func just gets temporarily inserted for top down re checking of main()"
    print("EARLY DEBUG exit(): " + message)
    exit()


def main():
    print("Model classes for tlog.py")


if __name__ == '__main__':
    main()
