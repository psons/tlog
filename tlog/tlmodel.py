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
import base64
import hashlib
import re

class TLogInternalException(Exception):
    'Tlog Internal Excption indicates a failed validation indicating a bug'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

blank_ln_pat = re.compile("^\s*$")

class Section:
	head_pat = re.compile("^#")

	def __init__(self, data = None):
		self.current_item = Item()
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
			i = Item()
			i.set_attrib(akey, aval)
			self.body_items.insert(0, i)


	@classmethod
	def fromtext(cls, text):
		"create a Section from multiline text paramater"
		new_section = Section()
		lines = text.split("\n")
		for line in lines:
			new_section.add_line(line)
		return new_section


	def add_line(self, data):
		"See doc under Document.add_line()"
		if Section.head_pat.match(data):
			#print("trying to add a section header data:", data)
			self.header = data
		else:
			if self.current_item.is_empty():
				#print("adding data to item that was empty:", data)
				self.current_item.add_line(data)
			else:
				if Item.head_pat.match(data):
					self.current_item = Item(data) #new Item
					self.body_items.append(self.current_item) #add to section body_items
				else:
					#print("gotta add the data to current item in section")
					self.current_item.add_line(data)
		return self.current_item

	def add_item(self, arg_item):
		if type(arg_item) is Item:
			need_append = True   
			for body_item in self.body_items:
				# todo this is partly like the merge logic needed.  If the "top"
				#  matches, it replaces the sub items.
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
		#print("DEBUG str(self.body_items):" + str(self.body_items))
		for item in self.body_items:
			if aString and not item.is_empty():
				aString += "\n"    # some markdowns want 2 '\n' here.
			if not item.is_empty():
				aString += str(item)
		#print("DEBUG aString:" + aString + ":after aString")
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
		for item in self.body_items[0:1]: # just first Item
			if not item.is_attrib_only():
				return False
		for item in self.body_items[1:]: # after first  Item
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
			#print("adding item:\n", str(other_item) )
			self.add_item(other_item)


	# def has_item(self, an_item):
	# 	for item in ...

	def update_progress(self):
		"""
		Make a list containing copies of the in_progress items in the section.
		Toggle the original items to unfinished.
		Return the list of copies.  

		"""
		#print("in Section:" + self.header)
		sec_in_progs = []
		for item in self.body_items:
			if Item.in_progress_pat.match(item.top):
				#print("\titem top:" + item.top)
				sec_in_progs.append(item.deep_copy())
				item.in_prog_2_unfin()
		#print("sec_in_progs:" + ",".join(map(str, sec_in_progs) ))
		return sec_in_progs 


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
		attmo = TLAttribute.attr_pat.match(data) # return attribute match object
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
	done_str = "^[xX] *-"
	done_pat = re.compile(done_str)
	in_progress_str = r'^[/\\] *-'
	in_progress_pat = re.compile(in_progress_str)

	unfinished_s = "u -"
	unfinished_str = "^[uU] *-"
	unfinished_pat = re.compile(unfinished_str)

	do_str = "^[dD] *-"
	do_pat = re.compile(do_str)

	head_str = "|".join([done_str, in_progress_str, do_str, unfinished_str])
	head_pat = re.compile(head_str)

	not_do_str = "|".join([done_str, in_progress_str, unfinished_str])
	not_do_pat = re.compile(not_do_str)

	leader_group_str = "(" + head_str + ")"
	title_group_str = r"\s*(.*\S)\s*$"
	top_parser_str = leader_group_str + title_group_str
	top_parser_pat = re.compile(leader_group_str + title_group_str)
	title_hash_attr_str = "titleHash"

	def __init__(self, data = None, subs = None, attrs = None):
		self.top = ""
		self.subs = subs or []
		self.attribs = attrs or dict()
		if data:
			self.add_line(data)

	# todo throw an error in Item if match Section.head_pat
	#  using this method to put ^# lines in an item would be confusing.
	#  (in normal document creation, ^# lines would be the header in the
	#  Section, and would never be inserting ito an Item in the Section)
	@classmethod
	def fromtext(cls, text):
		"""create an Item from multiline text parameter"""
		new_item = Item()
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
		#print("regex string:" + Item.top_parser_str + ":")
		item_top = self.top
		topmo = Item.top_parser_pat.match(item_top) # return top match object
		if topmo:
			return topmo.group(2)
		else:
			#print("does not match:" + item_top + ":")
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
		if Item.head_pat.match(data):
			self.top = data
		else:
			if not self.attrib_by_line(data):
				self.subs.append(data)

	def deep_copy(self):
		"""
		Makes a copy where 
		 - the top element refers to the same top string, which is ok
		   because strigs are immutable
		 - the subs list is copied to a new list.
		 - the attribute dictionary is copied to a new dict 
		"""
		return Item(data = self.top, subs = list(self.subs), attrs = dict(self.attribs))

	def is_empty(self):
		"return true if no header or body_items, else return false."
		boolean_return_of_Item_is_empty = (not self.top) and (not len(self.subs)) and (not len(self.attribs))
		return boolean_return_of_Item_is_empty

	def is_attrib_only(self):
		"return true if no header or body_items, else return false."
		boolean_return_of_is_attrib_only = (not self.top) and (not len(self.subs))
		return boolean_return_of_is_attrib_only

	def attribs_str (self):
		if len(self.attribs): 
			return "\n".join( sorted({ str(self.attribs[x]) for x in self.attribs.keys()})) 
		else:
			return ""

	def __str__(self):
		t = self.top if self.top else ""
		t += ("\n" if self.top and (len(self.attribs) or len(self.subs)) else "")
		t += self.attribs_str()
		t += ("\n" if len(self.attribs) and len(self.subs) else "")
		s = "\n".join(self.subs) if len(self.subs) != 0 else ""
		#print("DEBUG len(self.subs):" + str(len(self.subs)))
		#print("DEBUG t + s:" + t + s + ":after t + s")

		return t + s 

	# todo critique this approach.  more can be encapsulated
	#  make a transition method transition(fromPattern, toToken)
	#  transition(in_progress_pat, Item.unfinished_s)
	#  how should handle case where fromPattern does not match?
	def in_prog_2_unfin(self):
		r"""Changes the item's patten from '/' or '\' to 'u' """
		# self.top = re.sub(Item.in_progress_str, Item.unfinished_s, self.top)
		self.top = Item.in_progress_pat.sub(Item.unfinished_s, self.top)
		return self

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

	Any line beginning with d, D, x, X, /, \ is a task line.
		d, D - represent 'do' tasks, and get added to the document.backlog
		x, x - represent complete tasks and get added to the current Section
		/, \ - represent in progress tasks, and get added to the
				document.in_progress section with a copy changed to
				u - (unfinished) and added to the current section
	If a task line is followed by lines that are a bullet list, or free text,
	the additional lines should be kept together as paryt of the task Item object.

	Any line not that is not a Section or Item header gets added to the
	current Item.

	Items that begin a section, sometimes do not have a task line

	Support multiline backlog items.
	in_progress items beginning with /, \ will stay with section and be copied
	to the in_progress list.
	"""

	defautInProgHead = "#In progress"

	# need a constructor that takes a list of lines
	# todo - need tests for this
	def __init__(self, name = None, input_lines = None):
		"""
		Public interface Instance attributes:
			journal - the Sections and Items collected in past days
			in_progress - List of in progress Items to be put in the current day 
				document.
			backlog - Section containing 'do' Items.  

		"""
		# todo this is suspect
		# d - this is suspect when name is provided
		self._doc_name = name or ""

		self.journal = []
		self.in_progress = Section(None) # external logic sets to today
		self.backlog = Section()

		self.current_section = Section(None)		
		self.journal.append(self.current_section)
		self.last_add = self.current_section

		self.add_lines(input_lines)

	dname_attr_str = "DocName"

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

			data  = line.rstrip("\n") # todo: fix: stripping newline off blank line makes it not get in body_items.
			#print("add_lines data:" + data)
			self.add_line(data)

	def add_line(self, data):
		"""
		Add a single data line into the document according to
		patterns in the Item and Section classes.
		"""
		if Item.do_pat.match(data):
			self.backlog.add_line(data)
			self.last_add = self.backlog


		elif Section.head_pat.match(data):
			if self.current_section.is_empty():
				#Putting a header on initial section
				self.current_section.add_line(data)
				self.last_add = self.current_section
			else:
				#New section. 
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

	# todo implement
	def shorten_backlog(self, num_tasks=None):
		"""
		discard tasks in the backlog beyond num_tasks
		If max_tasks is set and num_tasks is not provided,
		use max_tasks as the number of tasks to keep.
		If neither is provided, keep all tasks.
		"""
		max_t = self.max_tasks or len(self.backlog.body_items)
		num_t = num_tasks or max_t
		num_t = int(num_t)
		self.backlog.body_items = list(self.backlog.body_items[0:num_t])
		pass
		return self


	def backlog_str(self):
		"""Return the backlog section as a string"""
		return str(self.backlog)

	def __str__(self):
		s =  self.journal_str() + "\n" 
		s += self.in_progress_str() + "\n" if not self.in_progress.is_empty() else ""
		s += self.backlog_str()
		return s

	def make_in_progress(self, in_prog_head = defautInProgHead ):
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
				self.journal = []
		else:
			self.journal = []

	def generate_backlog_title_hashes(self):
		self.backlog.save_item_title_hashes()

	def merge_backlog(self, other_backlog_section: Section):
		if other_backlog_section:
			for item in other_backlog_section.body_items:
				self.backlog.add_merge_item(item)
		else:
			print("DEBUG warning: other_backlog_section is None merging into " + self.doc_name)

def	debExit(message = ""):
	"This func just gets temporarily inserted for top down re checking of main()"
	print("EARLY DEBUG exit(): " + message)
	exit()


def main():
	print("Model classes for tlog.py")

if __name__ == '__main__':
	main()
