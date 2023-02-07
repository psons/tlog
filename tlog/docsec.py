"""
Composition: Classes that have a general purpose usage, free of application
semantics.
Application semantics are set by the calling code when SectionSortDoc, Section,
and Item objects are instantiated.
"""

import hashlib
import logging
import re
from typing import Pattern, Dict, List

from tlutil import digest


class Section:
    """
    A Section can be read and written as a single section of a Markdown document
    divided by H1 headings as identified be the regex "^#".
    A Section have no H1 heading, if for example the text appears before any H1
    in a document.  If the caller subsequently adds a line matching the markdown
    H1 pattern
    to the section, it will be treated as the H1 for the top of the section.
    (ie. the Section can have only heading)

    Any text that is not an H1 will be formed into a list of
    Item objects comprising the body of the Section.

    The Section Objects must be constructed with a regex pattern
    top_parser_pat, and any lines matching that pattern will cause
    creation of a new Item in the list of body items.  Any subsequent
    text will be added to the latest Item in the body item list.

    Text (if present) in the Section before any line matching
    top_parser_pat is treated as meta data of the section.

    The meta data may consist of text and/or Attributes and will be stored
    in the first Item in the list of body items.
    """

    head_pat = re.compile("^#")

    def __init__(self, item_top_parser_pat, data: str = None) -> None:
        if not isinstance(item_top_parser_pat, Pattern):
            raise TLogInternalException(
                "Section __init__ was not passed a Pattern as the first object")
        self.item_top_parser_pat = item_top_parser_pat
        self.current_item = Item(self.item_top_parser_pat)
        self.header = ""
        self.body_items = [self.current_item]
        if data:
            self.add_section_line(data)

    def deep_copy(self):
        """
        Makes a copy where
            - the header element refers to the same header string, which is ok
            because strings are immutable
            - the each element in the body_items is deep copied to a new list.
            - the attribute dictionary is copied to a new dict
        """
        return Section.fromtext(str(self))

    def get_body_data(self):
        """
        :return: the list of Items that are not metadata.
        """
        body_data = [body_item for body_item in self.body_items if body_item.has_top()]
        return body_data

    def get_section_attrib(self, key):
        """
        return section attribute matching key, or None
        The Section attributes are the attribs in the first Item (index 0)
        on the body_items list, only if that Item has no text in its 'top' member.
        """
        if len(self.body_items[0].top) == 0:
            return self.body_items[0].get_item_attrib(key)
        return None

    def set_sec_attrib(self, akey, aval):
        "Set Section attributes by putting them in an otherwise empty first Item in the body_items"
        if self.body_items[0].is_attrib_only():
            self.body_items[0].set_attrib(akey, aval)
        else:
            i = Item(self.item_top_parser_pat)
            i.set_attrib(akey, aval)
            self.body_items.insert(0, i)

    @classmethod
    def fromtext(cls, item_top_parser_pat, text):
        "create a Section from multiline text parameter"
        new_section = Section(item_top_parser_pat)
        lines = text.split("\n")
        for line in lines:
            new_section.add_section_line(line)
        return new_section

    def add_section_line(self, data):
        """
        Used for building up sections and items line by line from text strings.
        See doc under BlotterDocument.add_line()
        """
        if Section.head_pat.match(data):
            # print("trying to add a section header data:", data)
            self.header = data
        else:
            if self.current_item.is_empty():
                # print("adding data to item that was empty:", data)
                self.current_item.add_item_line(data)
            else:
                if self.item_top_parser_pat.match(data):
                    self.current_item = Item(self.item_top_parser_pat, data)  # new Item
                    self.body_items.append(self.current_item)  # add to section body_items
                else:
                    # print("gotta add the data to current item in section")
                    self.current_item.add_item_line(data)
        return self.current_item

    def add_item(self, arg_item, head_insert: bool = False):
        """
        Adds a Whole item to Section self.
        head_insert_true is used when building the default an_endeavor new task story.md from taskes added by the user
        in the j/td file with the reasoning that short term tasks captured are top priority immediate follow up,
        so they stay high priority until explicitly moved to a lower priority in the story file.

        otherwise, task adding is done in conventional head to tail order.
        """
        if type(arg_item) is Item:
            need_append = True

            # Sections are created with an empty first Item, which should be used if it is empty
            if self.body_items[0].is_empty():
                self.body_items[0] = arg_item
                return

            for body_item in self.body_items:
                if body_item.top == arg_item.top:
                    body_item.subs = list(arg_item.subs)
                    need_append = False

            if need_append:
                if head_insert:
                    self.body_items.insert(0, arg_item)
                else:
                    self.body_items.append(arg_item)
        else:
            raise TLogInternalException("Section.add_item was given a non-Item")

    def str_body(self):
        """
        Returns body_items items as a string.
        Prevents adding an extra newline if there is an empty Item.
        """
        aString = ""
        # print("DEBUG str(self.body_items):" + str(self.body_items))
        for item in self.body_items:
            if aString and not item.is_empty():
                aString += "\n"  # some markdowns want 2 '\n' here.
            if not item.is_empty():
                aString += str(item)
        # print("DEBUG aString:" + aString + ":after aString")
        return aString

    def __str__(self):
        # got to be a more concise way to do this.
        header_str = self.header if self.header else ""
        body_str = self.str_body()
        header_newline = "\n" if self.header and body_str else ""
        return header_str + header_newline + body_str

    def is_attrib_section(self):
        """
        :return: true if self is_empty or has only an attribute item
        """
        if self.header != "":
            return False
        for item in self.body_items[0:1]:  # just first Item
            if not item.is_attrib_only():
                return False
        for item in self.body_items[1:]:  # after first  Item
            if not item.is_empty():
                return False
        return True

    def is_empty(self):
        """return true if no header or the body_items list contains only empty Items"""
        if self.header != "":
            return False

        for item in self.body_items:
            if not item.is_empty():
                return False

        return True

    # get_num_items method that ignores meta data item or empty item
    def get_num_items(self):
        """
        :return: the number of non-metadata or empty items
        """
        count: int = 0
        for item in self.body_items:
            if not item.is_empty():
                count += 1
        return count



    def save_item_title_hashes(self):
        for item in self.body_items:
            if not item.is_attrib_only():
                item.save_title_hash()

    def add_all_missing_item_title_hash(self):
        """
        calls item.add_missing_title_hash() on all non attribute sections.
        :return: None
        """
        for item in self.body_items:
            if not item.is_attrib_only():
                item.add_missing_title_hash()

    def get_matching_items(self, pattern: Pattern[str]):
        """
        :param pattern: compiled re to use to select matching items
        :return: list of matching Items
        """
        matching_items = [ i  for i in self.body_items if pattern.match(i.top)]
        return matching_items

    def get_matching_item_by_attribute(self, akey, aval ):
        """
        Gets first item with a key and value matching attribute
        :param akey: attribute_key to use in comparison
        :param aval: attribute value indicating a match.
        :return: the matching Item from self.body_items
        """
        item: Item
        for item in self.body_items:
            item_attribute: ItemAttribute = item.get_item_attrib_holder(akey)
            if item_attribute:
                if item_attribute.value == aval:
                    return item_attribute
        return None


    def find_replace_item_by_titleHash(self, new_item):
        """
        search the self.body_items list for an item matching attribute_key and attribute_value
        :param new_item:
        :return: the item reference if found, or None.
        """
        hash_attr_str = Item.title_hash_attr_str
        value = new_item.get_item_attrib(hash_attr_str)
        index: int = 0
        item: Item
        for item in self.body_items:
            title_hash = item.get_title_hash()
            if title_hash == value:
                found = True
                print(f"found item matching {hash_attr_str} to replace")
                print(f"replacing item:\n{item}")
                print(f"with item:\n{new_item}")
                self.body_items[index] = new_item
                return item  # this is the old item.  is it of any use?
            index += 1
        return None

    def remove_item(self, item):
        """ remove item, from body_items using find_item(item) matching rules"""
        tag = "remove_item()"
        body_item = self.find_item(item)
        logging.debug(f"{tag}: try to remove find_item({id(item)}) return of self.find_item(item): {id(body_item)}")
        self.body_items.remove(body_item)

    def find_item(self, other_item):
        """Return a reference to the an item with a saved 'titleHash:' attribute or title matching item."""
        for item in self.body_items:
            item_sth = item.get_saved_title_hash()
            if item_sth:
                if item_sth == other_item.get_saved_title_hash():
                    return item
            else:
                if item.get_title() == other_item.get_title():
                    return item
        return None

    def add_item_merge_enhanced(self, other_item):
        """match on titleHash if found, but use title if the target object does not have a saved title hash"""
        match_existing_found = False
        for item in self.body_items:
            item_sth = item.get_saved_title_hash()
            # print("Section:add_item_merge:self.item", item.top)
            if item_sth:
                if item_sth == other_item.get_saved_title_hash():
                    match_existing_found = True
                    item.merge_parts(other_item)
            else:
                # item has no sth, so compare the part of the title without the leader.
                if item.get_title() == other_item.get_title():
                    item.merge_parts(other_item)
        if not match_existing_found:
            # print("adding item:\n", str(other_item) )
            self.add_item(other_item) # why does this put other_item at the beginning of the body_items list
        return self


    def select_modify_item_tops_by_pattern(self, in_progress_pat: re.Pattern, unfinished_s: str):
        """
        "Select" and return a list containing copies of items from this section that match in_progress_pat,
            and modify the items tops of the originally matched items with unfinished_s
        Return the list of copies.

        """
        # print("in Section:" + self.header)
        sec_in_progress_task_list = []
        for item in self.body_items:
            if in_progress_pat.match(item.top):
                # print("\titem top:" + item.top)
                sec_in_progress_task_list.append(item.deep_copy(self.item_top_parser_pat))
                item.modify_item_top(in_progress_pat, unfinished_s)
        # print("sec_in_progress_task_list:" + ",".join(map(str, sec_in_progress_task_list) ))
        return sec_in_progress_task_list


class TLogInternalException(Exception):
    'Tlog Internal Excption indicates a failed validation indicating a bug'

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ItemAttribute:
    "T Log Attribute"
    delim = ':'
    attr_str = r'^(\w+)' + delim + r'(.*)'
    attr_pat = re.compile(attr_str)

    def __init__(self, attr_name, attr_val):
        self.name = attr_name
        self.value = attr_val

    @classmethod
    def fromline(cls, data):
        "Create an attribute from a data line.  (e. g. a string read from a file)"
        attmo = ItemAttribute.attr_pat.match(data)  # return attribute match object
        if attmo:
            return ItemAttribute(attmo.group(1), attmo.group(2))
        else:
            return None

    def __str__(self):
        return str(self.name) + ItemAttribute.delim + str(self.value)


class Item:
    """
    See documentation for the BlotterDocument class
    """

    title_hash_attr_str = "titleHash"

    def __init__(self, top_parser_pat, data:str=None, subs:[str]=None, attrs:Dict[str, ItemAttribute]=None):
        self.top = ""
        self.subs = subs or []
        self.attribs = attrs or dict()
        self.top_parser_pat = top_parser_pat
        if data:
            self.add_item_line(data)

    @classmethod
    def fromtext(cls, top_parser_pat, text):
        """create an Item from multiline text parameter"""
        new_item = Item(top_parser_pat)
        lines = text.split("\n")
        for line in lines:
            new_item.add_item_line(line)
        return new_item

    def attrib_by_line(self, data):
        """
        If a data string can parse to make a TLAttribute,
        set it as an item attribute and return it.
        Else, return None
        """
        attr = ItemAttribute.fromline(data)
        if attr:
            self.attribs[attr.name] = attr
            return attr
        else:
            return None

    def get_item_attrib(self, akey):
        """
        return the value of the attribute object associated with akey
        or None if it is not defined.
        """
        attrib_obj = self.get_item_attrib_holder(akey)
        if attrib_obj:
            return attrib_obj.value
        else:
            return None

    def set_attrib(self, akey, aval):
        """Set Item attributes given akey and aval"""
        self.attribs[akey] = ItemAttribute(akey, aval)

    def get_item_attrib_holder(self, akey) -> ItemAttribute:
        """Get Item attrib for key, returning TLAttribute object that has both key and val"""
        if akey in self.attribs:
            return self.attribs[akey]
        else:
            return None

    def get_leader(self):
        """
        The leader is the task type leader without the title
        The object is assumed to have been constructed with a top_parser_pat pattern
        with at least 1 grouping in the regular expression.
        The grouping match will be returned if a valid leader is found
        otherwise None is returned.
        See also tldocument.find_status_name() which can find the semantic name for the leader returned by this
        method.
        """
        # print("regex string:" + Item.top_parser_str + ":")
        item_top = self.top
        topmo = self.top_parser_pat.match(item_top)  # return top match object
        if topmo:
            return topmo.group(1)
        else:
            return None

    def get_title(self):
        """
        The title is the top without any task type leader or trailing whitespace
        The object is assumed to have been constructed with a top_parser_pat pattern
        with at least 2 groupings in the regular expression.
        The second grouping match will be returned if a valid leader is found
        otherwise None is returned.
        """
        item_top = self.top
        topmo = self.top_parser_pat.match(item_top)  # return top match object
        if topmo:
            return topmo.group(2)
        else:
            return None

    # https://stackoverflow.com/questions/2510716/short-python-alphanumeric-hash-with-minimal-collisions
    def get_title_hash(self):
        """returns a hash of the title if there is a title
        otherwise returns an empty string"""
        my_title = self.get_title()
        if my_title:
            hex_digest_of_md5_of_byte_encode_of_title = digest(my_title)
            # print("hex md5 title: {}".format(hex_digest_of_md5_of_byte_encode_of_title))
            return hex_digest_of_md5_of_byte_encode_of_title[0:10]
        else:
            return ''

    def save_title_hash(self):
        """
        Saves the hash of the title as an attribute so title can be edited in the blotter
        without losing the ability to match it with an incoming story task
        """
        self.set_attrib(Item.title_hash_attr_str, self.get_title_hash())

    def get_saved_title_hash(self) -> ItemAttribute:
        """gets the saved attribute title hash, which can differ from the get_title_hash() """
        return self.get_item_attrib(Item.title_hash_attr_str)

    def add_missing_title_hash(self) -> None :
        """
        computes and sets a value for the 'titleHash:' attribute if it is not already set.
        :return: None
        """
        if not self.get_saved_title_hash():
            self.save_title_hash()

    def title_matches_hash(self):
        """returns True if the title and saved hash both exist and the hash of the
        title matches saved hash"""
        title = self.get_title()
        if not title:
            return False
        sth = self.get_saved_title_hash()
        if not sth:
            return False
        th = self.get_title_hash()
        return th == sth

    def add_item_line(self, data):
        """Add a line as either the top task, an attribute, or sub text"""
        if Section.head_pat.match(data):
            raise TLogInternalException(
                "Putting a Section.head_pat line inside a Item is not allowed: " +
                data)

        if self.top_parser_pat.match(data):
            self.top = data
        else:
            if not self.attrib_by_line(data):
                self.subs.append(data)

    def merge_parts(self, other_item):
        """
        updates self to match other_item (kind of the inverse of deep_copy)
        references to the original 'self' object will be unaffected.
        """
        self.top = other_item.top
        self.subs = list(other_item.subs)
        self.attribs = dict(other_item.attribs)


    def deep_copy(self, top_parser_pat):
        """
        Makes a copy where
         - the top element refers to the same top string, which is ok
           because strings are immutable
         - the subs list is copied to a new list.
         - the attribute dictionary is copied to a new dict
        """
        return Item(top_parser_pat, data=self.top, subs=list(self.subs), attrs=dict(self.attribs))

    def has_top(self):
        if self.top:
            return True
        return False

    def is_empty(self):
        "return true if no header or body_items, else return false."
        boolean_return_of_Item_is_empty = (not self.top) and (not len(self.subs)) and (not len(self.attribs))
        return boolean_return_of_Item_is_empty

    def is_attrib_only(self):
        "return true if no header or body_items, else return false."
        boolean_return_of_is_attrib_only = (not self.top) and (not len(self.subs))
        return boolean_return_of_is_attrib_only

    def attribs_str(self):
        if len(self.attribs):
            return "\n".join(sorted({str(self.attribs[x]) for x in self.attribs.keys()}))
        else:
            return ""

    def detail_str(self):
        return "\n".join(self.subs) if len(self.subs) != 0 else ""

    def __str__(self):
        t = self.top if self.top else ""
        t += ("\n" if self.top and (len(self.attribs) or len(self.subs)) else "")
        t += self.attribs_str()
        t += ("\n" if len(self.attribs) and len(self.subs) else "")
        s = self.detail_str()
        # print("DEBUG len(self.subs):" + str(len(self.subs)))
        # print("DEBUG t + s:" + t + s + ":after t + s")

        return t + s


    def modify_item_top(self, pattern, new_string):
        r"""
        Changes the item's patten to new_string.  i.e '/' or '\' to 'u'
        :param pattern:
        :param new_string:
        :return:
        """
        self.top = pattern.sub(new_string, self.top)
        return self


class SectionSortDoc:
    """
    This class is a parsing and sorting class.   Its categories are Sections, and data are added to those
     categories as Item objects under Section according to a dictionary initialized in the constructor.

    This class has no Dom,ain semantics, which are assumed to be known to the calling class when building
    SectionSortDoc Objects.

    The class BlotterDocument has the tlog semantics and uses this class.

    Goal: provide a structure where multiple leader types such as '^d - ' are associated with a
    single section instance

    Construction notes:
    initialize with nothing, but add pairs of #head_str, [list of leader strings]
    build: map of leader pattern -> Section instances for classifying
        <instead of adding to journal or backlog>
        adding each pair rebuilds the map
    need: access to the values of the map.  each #head_str has semantic meaning to the caller, tlog

    use:
    special_sections = SectionSortDoc('^#')
    special_sections.add_leader_entry('# Past Tasks', ['^[aA] *-', '^[xX] *-'])
    special_sections.add_leader_entry('# Current Tasks', ['^[dD] *-'])
    place_to_put = special_sections.insert_item("")

    Structure:
    The set of Section objects can be looked up through two different dictionaries.
     (1) The leader_instance_dict is used to classify Items by pattern into Section objects.
     It has keys that are regular expressions compiled from pattern strings (such as '^d - ') that the user provides
     to the add_leader_entry() method.  Each values is a reference to the Section objects that
     Items matching the regex keys should be added to. (See the insert_item() method )
     (2) The head_instance_dict can be used to find the Section objects by the section heading (for example '^#')

     as keys that the usThis is a set of Section objects that have references indexed into two dictionaries.

    """
    def __init__(self, header_pattern: Pattern, item_top_parser_pat: Pattern):
        # regex that defines what a header is.  Need for validation
        self.header_pat = header_pattern
        self.item_top_parser_pat = item_top_parser_pat
        self.head_leaders_dict: Dict[str, List[str]] = {} # do i need this?  maybe for error messages?
        self.head_instance_dict: Dict[str, Section] = {} # map string headers -> Section instances
        self.leader_instance_dict:[str, Section] = {} # for callers to add to the correct instances

    def add_leader_entry(self, heading: str, pattern_strs: List[Pattern[str]]):
        """
        Add an association between a list of leader pattern_strs and a heading and
        Section instance for that heading:
            each item in the pattern_strs list will be mapped to a Section object indexed
            by heading

        Will not support update of a heading once it is added.
        """
        if not self.header_pat.match(heading):
            raise TLogInternalException(f"heading {heading} does not match {self.header_str}")
        if heading in self.head_instance_dict:
            raise TLogInternalException(f"update of existing heading ({heading}) not supported")
        self.head_leaders_dict[heading] = pattern_strs
        self.head_instance_dict[heading] = Section(self.item_top_parser_pat, heading) # todo set item insert prefrence at head or tail as a new attribute of a section.
        for leader in pattern_strs:
            self.leader_instance_dict[re.compile(leader)] = self.head_instance_dict[heading]
            # print("compile re for {} is {}".format(leader, str(re.compile(leader))))

    def __repr__(self):
        return "\n".join([ str(leader) + " => " + self.leader_instance_dict[leader].header
                           + " (" + repr(self.leader_instance_dict[leader]) + ")"
                           for leader in self.leader_instance_dict.keys()])

    def __str__(self):
        ds = "\n".join([str(self.head_instance_dict[s]) for s in self.head_instance_dict.keys()])
        return ds

    def get_report_str(self, report_section_names: List[str]):
        """
        Given a list of section names, return the concatenated
        string representation if found in this SectionSortDoc
        """
        report_section_obj_list: List[Section] =  []
        for report_section in report_section_names:
            if report_section in self.head_instance_dict.keys():
                report_section_obj_list.append(self.head_instance_dict[report_section])
            else:
                raise TLogInternalException(
                    f"A section name was requested that is not part of SectionSortDoc {repr(self)}")
        return "\n\n".join([str(section) for section in report_section_obj_list])  # stringify the list of matches.
    def insert_item(self, item: Item):
        """
        Side effect: insert Item in first matching section in leader_instance_dict
        Return the instance from leader_instance_dict matching item.top or None"""
        for key_pat in self.leader_instance_dict.keys():
            if key_pat.match(item.top):
                section_match: Section = self.leader_instance_dict[key_pat]
                # section_match.add_item(item)
                section_match.add_item_merge_enhanced(item)
                return section_match
        return None