import hashlib
import re
from typing import Pattern, Dict


class Section:
    head_pat = re.compile("^#")

    def __init__(self, item_top_parser_pat, data: str = None) -> None:
        self.item_top_parser_pat = item_top_parser_pat
        self.current_item = Item(self.item_top_parser_pat)
        self.header = ""
        self.body_items = [self.current_item]
        if data:
            self.add_line(data)

    def deep_copy(self):
        """
        Makes a copy where
            - the header element refers to the same header string, which is ok
            because strings are immutable
            - the each element in the body_items is deep copied to a new list.
            - the attribute dictionary is copied to a new dict
        """
        return Section.fromtext(str(self))

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
            new_section.add_line(line)
        return new_section

    def add_line(self, data):
        "See doc under Document.add_line()"
        if Section.head_pat.match(data):
            # print("trying to add a section header data:", data)
            self.header = data
        else:
            if self.current_item.is_empty():
                # print("adding data to item that was empty:", data)
                self.current_item.add_line(data)
            else:
                if self.item_top_parser_pat.match(data):
                    self.current_item = Item(self.item_top_parser_pat, data)  # new Item
                    self.body_items.append(self.current_item)  # add to section body_items
                else:
                    # print("gotta add the data to current item in section")
                    self.current_item.add_line(data)
        return self.current_item

    def add_item(self, arg_item):
        if type(arg_item) is Item:
            need_append = True
            for body_item in self.body_items:
                if body_item.top == arg_item.top:
                    body_item.subs = list(arg_item.subs)
                    need_append = False

            if need_append:
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

    def save_item_title_hashes(self):
        for item in self.body_items:
            if not item.is_attrib_only():
                item.save_title_hash()

    def get_matching_items(self, pattern: Pattern[str]):
        """
        used by get_xa_...
        :param pattern: compiled re to use to select matching items
        :return:
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
            item_attribute: TLAttribute = item.get_item_attrib_holder(akey)
            if item_attribute:
                if item_attribute.value == aval:
                    return item_attribute
        return None

    def find_replace_item_by_titleHash(self, new_item):
        """
        search the self.body_items list for an item matching attribute_key and attribute_value
        :param new_item:
        :param akey:
        :param aval:
        :return:
        """
        hash_attr_str = Item.title_hash_attr_str
        value = new_item.get_item_attrib(hash_attr_str)
        index: int = 0
        item: Item
        for item in self.body_items:
            title_hash = item.get_title_hash()
            if title_hash == value:
                print(f"found item matching {hash_attr_str} to replace")
                print(f"replacing item:\n{item}")
                print(f"replacing item:\n{new_item}")
                self.body_items[index] = new_item
                return item  # this is the old item.  is it of any use?
            index += 1
        return None

    def add_merge_item(self, other_item):
        """
        Do this by title hash.  If the item is already included, it came from a story
        and has a title hash
        :param other_item:
        :return:
        """
        # print("Checking to see if item is in Section ", self.header)
        # print("Item is:", other_item.top)
        match_existing_found = False
        for item in self.body_items:
            item_sth = item.get_saved_title_hash()
            # print("Section:add_merge_item:self.item", item.top)
            if item_sth:
                if item_sth == other_item.get_title_hash():
                    # todo implement an item merge to call from here
                    # print("matching hashes found. ")
                    match_existing_found = True
        if not match_existing_found:
            # print("adding item:\n", str(other_item) )
            self.add_item(other_item)

    # def has_item(self, an_item):
    # 	for item in ...

    def update_progress(self, in_progress_pat, unfinished_s):
        """
        Make a list containing copies of the in_progress items in the section.
        Toggle the original items to unfinished.
        Return the list of copies.

        """
        # print("in Section:" + self.header)
        sec_in_progs = []
        for item in self.body_items:
            if in_progress_pat.match(item.top):
                # print("\titem top:" + item.top)
                sec_in_progs.append(item.deep_copy(self.item_top_parser_pat))
                item.in_prog_2_unfin(in_progress_pat, unfinished_s)
        # print("sec_in_progs:" + ",".join(map(str, sec_in_progs) ))
        return sec_in_progs


class TLogInternalException(Exception):
    'Tlog Internal Excption indicates a failed validation indicating a bug'

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TLAttribute:
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
        attmo = TLAttribute.attr_pat.match(data)  # return attribute match object
        if attmo:
            return TLAttribute(attmo.group(1), attmo.group(2))
        else:
            return None

    def __str__(self):
        return str(self.name) + TLAttribute.delim + str(self.value)


class Item:
    """
    See documentation for the Document class
    """

    title_hash_attr_str = "titleHash"

    def __init__(self, top_parser_pat, data:str=None, subs:[str]=None, attrs:Dict[str, TLAttribute]=None):
        self.top = ""
        self.subs = subs or []
        self.attribs = attrs or dict()
        self.top_parser_pat = top_parser_pat
        if data:
            self.add_line(data)

    @classmethod
    def fromtext(cls, top_parser_pat, text):
        """create an Item from multiline text parameter"""
        new_item = Item(top_parser_pat)
        lines = text.split("\n")
        for line in lines:
            new_item.add_line(line)
        return new_item

    def attrib_by_line(self, data):
        """
        If a data string can parse to make a TLAttribute,
        set it as an item attribute and return it.
        Else, return None
        """
        attr = TLAttribute.fromline(data)
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
        self.attribs[akey] = TLAttribute(akey, aval)

    def get_item_attrib_holder(self, akey):
        """Get Item attrib for key, returning TLAttribute object that has both key and val"""
        if akey in self.attribs:
            return self.attribs[akey]
        else:
            return None

    def get_title(self):
        """
        The title is the top without any task type leader or trailing whitespace
        """
        # print("regex string:" + Item.top_parser_str + ":")
        item_top = self.top
        topmo = self.top_parser_pat.match(item_top)  # return top match object
        if topmo:
            return topmo.group(2)
        else:
            # print("does not match:" + item_top + ":")
            return None

    # https://stackoverflow.com/questions/2510716/short-python-alphanumeric-hash-with-minimal-collisions
    def get_title_hash(self):
        """returns a hash of the title if there is a title
        otherwise returns an empty string"""
        my_title = self.get_title()
        if my_title:
            my_bytes = my_title.encode('utf-8')
            md5_of_bytes = hashlib.md5(my_bytes)
            hex_digest_of_md5_of_byte_encode_of_title = md5_of_bytes.hexdigest()
            # print("hex md5 title: {}".format(hex_digest_of_md5_of_byte_encode_of_title))
            return hex_digest_of_md5_of_byte_encode_of_title[0:10]
        else:
            return ''

    def save_title_hash(self):
        """
        Saves the hash of the title as an attribute so title can be edited in the journal
        without loosing the ability to match it with an incoming story task
        """
        self.set_attrib(Item.title_hash_attr_str, self.get_title_hash())

    # todo make saved title hash available as a read only property to
    #  be consistent with notes in  Module and Object strategy.md
    def get_saved_title_hash(self):
        """gets the saved attribute title hash, which can differ from the get_title_hash() """
        return self.get_item_attrib(Item.title_hash_attr_str)

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

    def add_line(self, data):
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

    def deep_copy(self, top_parser_pat):
        """
        Makes a copy where
         - the top element refers to the same top string, which is ok
           because strigs are immutable
         - the subs list is copied to a new list.
         - the attribute dictionary is copied to a new dict
        """
        return Item(top_parser_pat, data=self.top, subs=list(self.subs), attrs=dict(self.attribs))

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

    def __str__(self):
        t = self.top if self.top else ""
        t += ("\n" if self.top and (len(self.attribs) or len(self.subs)) else "")
        t += self.attribs_str()
        t += ("\n" if len(self.attribs) and len(self.subs) else "")
        s = "\n".join(self.subs) if len(self.subs) != 0 else ""
        # print("DEBUG len(self.subs):" + str(len(self.subs)))
        # print("DEBUG t + s:" + t + s + ":after t + s")

        return t + s

    # see commentary in Module and Object strategy.md
    # replace with transform_top which should pass in the pattern and the replacement string
    def in_prog_2_unfin(self, in_progress_pat, unfinished_s):
        r"""Changes the item's patten from '/' or '\' to 'u' """
        self.top = in_progress_pat.sub(unfinished_s, self.top)
        return self