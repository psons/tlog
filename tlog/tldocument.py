#!/usr/local/bin/python3
"""
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
from typing import List, Dict, Pattern

from docsec import Section, TLogInternalException, Item

blank_ln_pat = re.compile("^\s*$")


class Document:
    """
    Document objects are made from lists of text lines to be made into Sections
    and Items, with special handling for 'do' Items and 'in progress' Items.

    The 'do' items are immediately extracted to a backlog section when lines are
    added to the document.
    The 'in progress' items are initially just loaded to their sections.  A
    make_in_progress method is provided to copy the in progress items to a section
    initially named '#In progress' to represent tasks planned for the next day or
    week, or agile sprint, or whatever period.

    Any line beginning with d, D, x, X,  /, \ is a task line.
        d, D - represent 'do' tasks, and get added to the document.backlog
        x, x - represent complete tasks and get added to the current Section
        /, \ - represent in progress tasks, and get added to the
                document.in_progress section with a copy changed to
                u - (unfinished) and added to the current section
    If a task line is followed by lines that are a bullet list, or free text,
    the additional lines will be kept together as part of the task Item object.

    Any input text line line not that is not a Section or Item header gets added to the
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
    defautInProgHead = "#In progress"
    dname_attr_str = "DocName"

    # need a constructor that takes a list of lines
    # todo - need tests for this
    def __init__(self, name=None, input_lines=None, day=None):
        """
        Public interface Instance attributes:
            journal - the Sections and Items collected in past days
            in_progress - List of in progress Items to be put in the current day
                document.
            backlog - Section containing 'do' Items.

        """
        domth: str = day if day else ""
        current_task_head = f'# Current Tasks {domth}'
        self.past_task_head = '# Past Tasks'
        self.scrum = DocStructure(Section.head_pat)
        self.scrum.add_leader_entry(self.past_task_head, [Item.abandoned_pat,
                                                          Item.completed_pat, Item.unfinished_pat])
        self.scrum.add_leader_entry(current_task_head, [Item.in_progress_pat, Item.do_pat])

        self._doc_name = name or ""

        self.initialize_journal()

        self.add_lines(input_lines)

    def initialize_journal(self):
        """
        Initializes the journal list of sections to make sure a section at jornal[0]
        and a current section
        """
        self.journal = []
        self.in_progress = Section(None)  # external logic sets to today
        self.backlog = Section()
        self.current_section = Section(None)
        self.journal.append(self.current_section)
        self.last_add = self.current_section

    def _get_doc_name(self):
        "getter for doc_name"
        return self.get_doc_attrib(Document.dname_attr_str)

    def _set_doc_name(self, name):
        "setter for doc_name"
        self.set_doc_attrib(Document.dname_attr_str, name)

    doc_name = property(_get_doc_name, _set_doc_name)

    max_tasks_attr_str = "maxTasks"

    def _get_max_tasks(self):
        "getter for maxTasks"
        return self.get_doc_attrib(Document.max_tasks_attr_str)

    def _set_max_tasks(self, max):
        "setter for doc_name"
        self.set_doc_attrib(Document.max_tasks_attr_str, max)

    max_tasks = property(_get_max_tasks, _set_max_tasks)

    # todo - need tests for this
    def add_lines(self, r_lines):
        """
        make sections, which contain items
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
        if Item.do_pat.match(data):
            self.backlog.add_line(data)
            self.last_add = self.backlog


        elif Section.head_pat.match(data):
            if self.current_section.is_empty():
                # Putting a header on initial section
                self.current_section.add_line(data)
                self.last_add = self.current_section
            else:
                # New section.
                self.current_section = Section(data)
                self.journal.append(self.current_section)
                self.last_add = self.current_section

        elif Item.not_do_pat.match(data):
            self.current_section.add_line(data)
            self.last_add = self.current_section
        else:
            self.last_add.add_line(data)

    @classmethod
    def fromtext(cls, text):
        "create a Document from multiline text paramater"
        new_document = Document()
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
            s = Section()
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

    # coupled to:
    #   Item.done_pat which matches the xa.
    #   self.past_task_head.
    # would like to push these Story and task semantics out to the caller.
    def get_xa_story_tasks(self, story_key: str):
        """
        get tasks from the scrum that have a storySource: attribute
        and are complete or abandoned.
        """
        past_section: Section = self.scrum.head_instance_dict[self.past_task_head]
        xa_items = past_section.get_matching_items(Item.done_pat)
        xa_items_w_stories  = [ i for i in xa_items if i.get_item_attrib(story_key)]
        print(f"xa_items:\n{xa_items}")
        return xa_items_w_stories

        # get_matching_items(pattern: Pattern[str])

    # todo check to see if this is still used.
    #  Its only used in a test.
    def get_backlog_list(self, num_tasks=-1):
        """Typically the caller will pass in the self.max_tasks value,
        or take the default -1 indicating all tasks
        :return num_tasks entries from the backlog task list
        """
        num_tasks = int(num_tasks)
        if num_tasks == -1:
            return self.backlog
        if len(self.backlog.body_items) >= num_tasks:
            return self.backlog.body_items[0:num_tasks]
        else:
            return self.backlog.body_items

    def attribute_all_backlog_items(self, key, val):
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

    def shorten_backlog_deprecated(self, num_tasks=None):
        """
        todo delete this after the replacement above is working
        discard tasks in the backlog beyond num_tasks
        If max_tasks is set and num_tasks is not provided,
        use max_tasks as the number of tasks to keep.
        If neither is provided, keep all tasks.
        """
        max_t = self.max_tasks or len(self.backlog.body_items)
        num_t = num_tasks or max_t
        num_t = int(num_t)
        self.backlog.body_items = list(self.backlog.body_items[0:num_t])
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
        return a DocumetStructure with two sections representing part of
        what a scrum team member should report at the standup:
         - what did I accomplish yesterday: '# Past Tasks'
         - what will I work on today: '# Current Tasks'

         This method assumes make_in_progress() has already been called to make and
         'u - ' unfinished copy of any '/ - ' in progress items.
         """
        self.add_scrum_items(self.in_progress)  # / tasks from in_progress
        self.add_scrum_items(self.backlog)  # d tasks from backlog
        for section in self.journal:        # u, a, and x tasks from journal
            print("tmpdebug - section", section)
            # todo do this also for the special backlog section.  (extract a method)
            self.add_scrum_items(section)

        return self.scrum

    def add_scrum_items(self, section):
        for item in section.body_items:
            category_section: Section = self.scrum.insert_item(item)
            if category_section is None:
                print(f"tmpdebug for Section head '{section.header}', uncategorized - item", item)

    def make_in_progress(self, in_prog_head=defautInProgHead):
        """
        If in_prog_head exists in the self.journal,
            take it out of the journal and make it the in_progress section.

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
            self.in_progres = journal_section  # todo: potential major bug in the variable misspelling here!
            self.journal.remove(journal_section)
        else:
            self.in_progress.add_line(in_prog_head)

        for section in self.journal:
            for item in section.update_progress():
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

    def update_journal_item(self, item, attribute_key):
        """
        find matching hash Item in a journal section, and replace
        it with item
        return: the containing section that was updated or None if
        no section was updated
        """
        index = 0
        for section in self.journal:
            replaced_item = section.find_replace_item_by_titleHash(item)
            if replaced_item:
                return section
        return self.backlog.find_replace_item_by_titleHash(item)


    def generate_backlog_title_hashes(self):
        self.backlog.save_item_title_hashes()

    def merge_backlog(self, other_backlog_section: Section):
        if other_backlog_section:
            for item in other_backlog_section.body_items:
                self.backlog.add_merge_item(item)
        else:
            print("DEBUG warning: other_backlog_section is None merging into " + self.doc_name)

class DocStructure:
    """
    ----------------
    This is a partial step slightly in the direction making Section and
    Item be a generic by extracting the Section *header* and Item *header*
    patterns out to an encompassing Doc.   It is not quite right for reading
    story docs because it is going in the direction of inserting things into
    named sections by item Leader type.  This is good for Journal Documents
    (see "use:" below)  Stories should keep Items under the Sections they
    appear in.  The value is to be able to load a Document as a Story, and
    extract the specialized sections by leader type.
    The existing Document code suitable for loading stories just needs to know if
    a particular pattern means a new Section or Item grouping should be
    started as a series of lines is read.
    ----------------
    Goal: provide a structure where multiple leader types such as '^d - ' are associated with a
    single section instance

    Construction notes:
    initialize with nothing, but add pairs of #head_str, [list of leader strings]
    build: map of leader pattern -> Section instances for classifying
        <instead of adding to journal or backlog>
        adding each pair rebuilds the map
    need: access to the values of the map.  each #head_str has semantic meaning to the caller, tlog

    use:
    special_sections = DocStructure('^#')
    special_sections.add_leader_entry('# Past Tasks', ['^[aA] *-', '^[xX] *-'])
    special_sections.add_leader_entry('# Current Tasks', ['^[dD] *-'])
    place_to_put = special_sections.insert_item("")
    """
    def __init__(self, header_pattern_str: str):
        # regex that defines what a header is.  Need for validation
        self.header_str = header_pattern_str
        self.header_pat = re.compile(self.header_str)
        self.head_leaders_dict: Dict[str, List[str]] = {} # do i need this?  maybe for error messages?
        self.head_instance_dict: Dict[str, Section] = {} # map string headers -> Section instances
        self.leader_instance_dict:[str, Section] = {} # for callers to add to the correct instances


    def add_leader_entry(self, heading: str, pattern_strs: List[Pattern[str]]):
        """
        Add an association between a list of leader pattern_strs and a heading and
        Section instance for that heading
        Will not support update of a heading once it is added.
        """
        if not self.header_pat.match(heading):
            raise TLogInternalException(f"heading {heading} does not match {self.header_str}")
        if heading in self.head_instance_dict:
            raise TLogInternalException(f"update of existing heading ({heading}) not supported")
        self.head_leaders_dict[heading] = pattern_strs
        self.head_instance_dict[heading] = Section(heading)
        for leader in pattern_strs:
            self.leader_instance_dict[re.compile(leader)] = self.head_instance_dict[heading]
            #print("compile re for {} is {}".format(leader, str(re.compile(leader))))

    def __repr__(self):
        return "\n".join([ str(leader) + " => " + self.leader_instance_dict[leader].header
                           + " (" + repr(self.leader_instance_dict[leader]) + ")"
                           for leader in self.leader_instance_dict.keys()])

    def __str__(self):
        ds = "\n".join([str(self.head_instance_dict[s]) for s in self.head_instance_dict.keys()])
        return ds


    def insert_item(self, item: Item):
        """
        Side affect: insert Item in first matching section in leader_instance_dict
        Return the instance from leader_instance_dict matching item.top or None"""
        for key_pat in self.leader_instance_dict.keys():
            if key_pat.match(item.top):
                section_match: Section = self.leader_instance_dict[key_pat]
                section_match.add_item(item)
                return section_match
        return None


def debExit(message=""):
    "This func just gets temporarily inserted for top down re checking of main()"
    print("EARLY DEBUG exit(): " + message)
    exit()


def main():
    print("Model classes for tlog.py")


if __name__ == '__main__':
    main()
