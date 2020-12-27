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
    backlog - special section built by adding all the unresolved tasks from the journal sections.
    scrum   - a DocStructure object with 
                - a section for Resolved tasks. (heading '# Resolved {day of month}' ) 
                - a Section with a limited number of tasks for current work session (heading '# To Do {day of month}')
"""

class TLDocument:
    """
    Document objects are made from lists of text lines to be made into Sections
    and Items, with special handling for 'do' Items and 'in progress' Items.

    The 'do' items are immediately extracted to a backlog section when lines are
    added to the document.
    The 'in progress' items are initially just loaded to their sections.  A
    make_in_progress method is provided to copy the in progress items to a section
    initially named '#In progress' to represent tasks that have begun, but are not complete.

    Any line beginning with d, D, x, X,  /, \ is a task line.
        d, D - represent 'do' tasks, and get added to the document.backlog
        x, x - represent complete tasks and get added to the current Section
        /, \ - represent in progress tasks, and get added to the
                document.in_progress section with a copy changed to
                u - (unfinished) and added to the current section
    If a task line is followed by lines that are a bullet list, or free text,
    the additional lines will be kept together as part of the task Item object.

    Any input text line line that is not a Section or Item header gets added to the
    current Item.

    Items that begin a section, sometimes do not have a task line

    Support multiline backlog items.

    in_progress items beginning with /, \ will stay with section and be copied
    to the in_progress list make_in_progress is run.

    Attributes are supported using the class TLAttribute

    Some attributes are supported as properties in the Document class and
    implemented as Attributes on a special first section:
        doc_name DocName: ((read / write)
        max_tasks maxTasks: todo someday implement max_tasks property

    The Section and Item classes can be injected with attributes, but
    they should be optional in most or all cases.

    ## Evolution:
    The class Document should be refactored over time to hold any semantic meaning for the
    documents needed by tlog. Perhaps a class name TLDocument.

    The 'journal' should evolve to be created of Sections and Items *as read from disk*.
    The name journal may not make sense anymore, and this could be a list
    named document_sections in a generic Document class free of TLog semantics,
    possibly just being a Markdown Document.
    todo someday refactor to leave the backlog tasks in the journal, and build it with a separate
    processing method, like make_in_progress, the goal being a general; purpose Document

    The class DocStructure should be used to associate Item leader types
    with semantically meaningful special sections like Backlog and In_Progress.

    """
    default_maxTasks = 1 # used if not specified in a story.txt
    default_initial_task_capacity = 5  # default number of backlog tasks to take into a day sprint

    defautInProgHead = "#In progress"
    dname_attr_str = "DocName"

    # Item and leader related settings:
    abandoned_str = "^[aA] *-"
    abandoned_pat = re.compile(abandoned_str)
    completed_str = "^[xX] *-"
    completed_pat = re.compile(completed_str)
    done_str = "|".join([completed_str, abandoned_str])
    done_pat = re.compile(done_str)  # Used externally in in TLDocument get_xa ..

    in_progress_str = r'^[/\\] *-' # used here in head_str and not_do_str
    in_progress_pat = re.compile(in_progress_str) # used in Item in modify_item_top() that i am refactoring

    unfinished_s = "u -"  # used in Item in modify_item_top() that i am refactoring
    unfinished_str = "^[uU] *-"
    unfinished_pat = re.compile(unfinished_str)  # used in test for Item in modify_item_top() that i am refactoring
                                                # Good usage in Document to configures the scrum Docstruct
    do_str = "^[dD] *-"  # used here as part of head_str
    do_pat = re.compile(do_str)  # Good usages in TLDocument to make scrum and add_line()

    head_str = "|".join([done_str, in_progress_str, do_str, unfinished_str])  # used here in head_pat and leader_group_str
    head_pat = re.compile(head_str)

    not_do_str = "|".join([done_str, in_progress_str, unfinished_str])  # just used here
    not_do_pat = re.compile(not_do_str)  # only used in Document

    leader_group_str = "(" + head_str + ")" # only used here
    title_group_str = r"\s*(.*\S)\s*$"  # only used here
    # top_parser_str = leader_group_str + title_group_str
    top_parser_pat = re.compile(leader_group_str + title_group_str)

    # need a constructor that takes a list of lines
    # todo - need tests for this
    def __init__(self, name=None, input_lines=None, day=None,
                 initial_task_capacity=default_initial_task_capacity):
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
        self.backlog = Section(TLDocument.top_parser_pat)
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

            data = line.rstrip("\n")  # todo: fix: stripping newline off blank line makes it not get in body_items.
            # print("add_lines data:" + data)
            self.add_line(data)

    def add_line(self, data):
        """
        Add a single data line into the document according to
        pattern_strs in the Item and Section classes.
        """
        if data is None:
            return
        if TLDocument.do_pat.match(data):
            self.backlog.add_line(data)
            self.last_add = self.backlog


        elif Section.head_pat.match(data):
            if self.current_section.is_empty():
                # Putting a header on initial section
                self.current_section.add_line(data)
                self.last_add = self.current_section
            else:
                # New section.
                self.add_section_from_line(data)

        elif TLDocument.not_do_pat.match(data):
            self.current_section.add_line(data)
            self.last_add = self.current_section
        else:
            self.last_add.add_line(data)

    def add_section_from_line(self, data: str):
        """

        :param data: tring to create a section
        :return:
        """
        self.current_section = Section(TLDocument.top_parser_pat, data)
        self.journal.append(self.current_section)
        self.last_add = self.current_section
        return self.current_section

    @classmethod
    def fromtext(cls, text):
        "create a Document from multiline text paramater"
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

    # todo: change ti approach where ('x - ', 'a -') with storySource get removed from the original story...
    #   and go into
    def get_xa_story_tasks(self, story_key: str):
        """
        get tasks from the scrum that have a 'storySource:' attribute
        and are complete ('x - ') or abandoned ('a -').
        """
        past_section: Section = self.scrum.head_instance_dict[self.resolved_section_head]
        xa_items = past_section.get_matching_items(TLDocument.done_pat)
        xa_items_w_stories  = [ i for i in xa_items if i.get_item_attrib(story_key)]
        return xa_items_w_stories

        # get_matching_items(pattern: Pattern[str])

    #  This is only only used in a test, and could be moved.
    def get_backlog_list(self, num_tasks=-1):
        """Typically the caller will pass in the self.max_tasks value,
        or take the default -1 indicating all tasks
        :return num_tasks entries from the backlog task list
        """
        num_tasks = int(num_tasks)
        if num_tasks == -1:
            return self.backlog.body_items
        if len(self.backlog.body_items) >= num_tasks:
            return self.backlog.body_items[0:num_tasks]
        else:
            return self.backlog.body_items

    def attribute_all_backlog_items(self, key, val):
        """creates attribute on every item in the backlog section.
        Useful for putting the storySource attribute on all the items read out of a story.
        :key the name of the attribute to set.
        :val the value to set for the attribute.
        """
        for item in self.backlog.body_items:
            item.set_attrib(key, val)


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

    def shorten_backlog(self, num_tasks=None):
        """
        discard extra tasks in the backlog section
        """
        self.backlog.body_items = self.shorten_task_list(
            self.backlog.body_items, num_tasks)
        return self

    def backlog_str(self):
        """Return the backlog section as a string"""
        return str(self.backlog)

    def __str__(self):
        s = self.journal_str() + "\n"
        s += self.in_progress_str() + "\n" if not self.in_progress.is_empty() else ""
        s += self.backlog_str()
        return s

    def make_scrum(self):
        """
        return a DocumentStructure with two sections representing part of
        what a scrum team member should report at the standup:
         - what did I accomplish yesterday: '# Past Tasks'
         - what will I work on today: '# Current Tasks'

         This method assumes make_in_progress() has already been called to make and
         'u - ' unfinished copy of any '/ - ' in progress items.
         """
        self.add_scrum_items(self.in_progress)  # / tasks from in_progress
        self.add_scrum_items(self.backlog)  # d tasks from backlog
        for section in self.journal:        # u, a, and x tasks from journal
            # todo do this also for the special backlog section.  (extract a method)
            self.add_scrum_items(section)

        return self.scrum

    def add_scrum_items(self, section):
        for item in section.body_items:
            category_section: Section = self.scrum.insert_item(item)
            # if category_section is None:
            #     print(f"tmpdebug for Section head '{section.header}', uncategorized - item", item)

    def make_in_progress(self, in_prog_head=defautInProgHead):
        """
        If in_prog_head exists in the self.journal,
            take it out of the journal and make it the in_progress section in self TLDocument

        loop through Sections in the Document
            loop through Items in the Sections,
            if data is a in_progress item
                make a copy of it.
                add the copy to the in_progress section.
                modify the original to 'unfinished'
        Elsewhere, set the header on the in_progress section.
        """
        existing_in_prog = False
        for journal_section in self.journal:
            if journal_section.header == in_prog_head:
                self.in_progress = journal_section
                existing_in_prog = True
                break
        if existing_in_prog:
            # this Section might have 'x - ', and other Items
            # that need to be preserved, as  for runs when user
            # has already completed some work for the day.
            #self.in_progress = journal_section
            self.journal.remove(journal_section)
        else:
            self.in_progress.add_line(in_prog_head)

        pat: re.Pattern = TLDocument.in_progress_pat
        for section in self.journal:
            for item in section.select_modify_item_tops_by_pattern(pat, TLDocument.unfinished_s):
                self.in_progress.add_item(item)

    def drop_journal(self):
        if len(self.journal) > 1:
            firstSection = self.journal[0]
            if firstSection.is_attrib_section():
                self.journal = [firstSection]
            else:
                self.initialize_journal()
        else:
            self.initialize_journal()

    # backlog vs journal.
    # journal is a list of sections with items is is read from a file.

    def insert_update_journal_item(self, item, default_section_heading="# New items"):
        """
        Search all Sections in the Journal list for an Item with a 'titleHash:' attribute value matching item.
            if a match is found in the journal, replace the matched Item with item.
        !! Paul removed the update of the backlog from this method. 2020-12-24.
        return: self
        """
        index = 0
        for section in self.journal:
            replaced_item = section.find_replace_item_by_titleHash(item)
            if replaced_item:
                break
        if not replaced_item:
            self.insert_new_item_into_journal_section(default_section_heading, item)
        return self

    def insert_new_item_into_journal_section(self, section_heading: str, item: Item):
        """
        add item into the journal section matching section_heading.
        Create a matching the section if necessary.
        """
        #todo add a section to contain the new item. or use an already existing '# New' section. needed by insert_update_journal_item
        added_item: bool = False
        for section in self.journal:
            if section.header == section_heading:
                section.add_item(item)
                added_item = True
        if not added_item:
            new_section: Section = self.add_section_from_line(section_heading)
            new_section.add_item(item)

    def generate_backlog_title_hashes(self):
        self.backlog.save_item_title_hashes()

    def merge_backlog(self, other_backlog_section: Section):
        # todo: enforce a configurable max of how many tasks go into backlog.
        if other_backlog_section:
            for item in other_backlog_section.body_items:
                self.backlog.add_merge_item(item)
        else:
            print("DEBUG warning: other_backlog_section is None merging into " + self.doc_name)


def debExit(message=""):
    "This func just gets temporarily inserted for top down re checking of main()"
    print("EARLY DEBUG exit(): " + message)
    exit()


def main():
    print("Model classes for tlog.py")


if __name__ == '__main__':
    main()
