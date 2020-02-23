#!/usr/local/bin/python3
"""
There is allways a curent Section in a Document.
There is allways a current Item in a Section.

If data is a section header, 
and 
	if the curent section is empty, use it
	else make a new curent section with the data.
If data is an item header other than 'do', 
	add it to the curent section.
	adding an item to a Section will:
		if the curent item is empty, use it.
		else make a new curent Item with the data.
		return a new curent_item
else if data is a 'do' item header 
	add it to the backlog Section
else 

""" 
#import pdb
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
		self.body = [ self.current_item ]
		if data:
			self.add_line(data)

	#todo add test for this.
	def deep_copy(self):
		return Section.fromtext(str(self))
		# """
		# Makes a copy where 
		#  - the header element refers to the same header string, which is ok
		#    because strigs are immutable
		#  - the each element in the body is deep copied to a new list.
		#  - the attribute dictionary is copied to a new dict 
		# """
		# the_copy = Section(data = self.header
		# for item in self.body:
		# 	#todo finish this for, maybe as a list coprehension
		# return the_copy


	def get_attrib(self, key):
		"""
		return section attribute matching key, or None
		The Section attributes are the attribs in the first Item (index 0) 
		on the body list, only if that Item has no text in its 'top' member. 
		"""
		if len(self.body[0].top) == 0:
			if  key in self.body[0].attribs:
				return self.body[0].attribs[key]
		return None

	def set_attrib(self, akey, aval):
		"Set Section attributes by putting then in an otherwise empty first Item in the body"
		if self.body[0].is_attrib_only():
			self.body[0].set_attrib(akey, aval)
		else:
			i = Item()
			i.set_attrib(akey, aval)
			self.body.insert(0, i)


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
					self.body.append(self.current_item) #add to section body
				else:
					#print("gotta add the data to curent item in section")
					self.current_item.add_line(data)
		return self.current_item

	def add_item(self, arg_item):
		if type(arg_item) is Item:
			need_append = True   
			for body_item in self.body:
				if body_item.top == arg_item.top:
					body_item.subs = list(arg_item.subs)
					need_append = False

			if need_append:
				self.body.append(arg_item)
		else:
			raise TLogInternalException("Section.add_item was given a non-Item")

	def str_body(self):
		"""
		Returns body items as a string.
		Prevents adding an extra newline if there is an empty Item.
		"""
		aString = ""
		#print("DEBUG str(self.body):" + str(self.body))
		for item in self.body:
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
		for item in self.body[0:1]: # just first Item
			if not item.is_attrib_only():
				return False
		for item in self.body[1:]: # after first  Item
			if not item.is_empty():
				return False
		return True


	def is_empty(self):
		"return true if no header or the body list contains only empty Items"
		if self.header != "":
			return False

		for item in self.body:
			if not item.is_empty():
				return False
	
		return True 

	def update_progress(self):
		"""
		Make a list containing copies of the in_progress items in the section.
		Toggle the original items to unfinished.
		Return the list of copies.  

		"""
		#print("in Section:" + self.header)
		sec_in_progs = []
		for item in self.body:
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
		"Create an atribute from a data line.  (e. g. a string read from a file)"
		attmo = TLAttribute.attr_pat.match(data) # return attribute match object
		if attmo:
			return TLAttribute(attmo.group(1), attmo.group(2))
		else:
			return None

	def __str__(self):
		return str(self.name) + TLAttribute.delim + str(self.value)

class Item:
	"""
	todo - move this documentation to the Document class
	Any thing beginning with d, D, x, X, /, \ followed by bullet list should be
	kept together.  
		d, D - represent do, and get added to the document.backlog
		x, x - represent complete and get added to the curent Section
		/, \ - represent in progress, and get added to the 
				document.in_progres copied to u - and added to the curent 
				section
	Any line not that is not a Section or Item header gets added to the 
	current Item. 

	Support multiline backlog items.
	in_progress items beginning with /, \ will stay with section and be copied 
	to the in_progress list.
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


	def __init__(self, data = None, subs = None, attrs = None):
		self.top = ""
		self.subs = subs or []
		self.attribs = attrs or dict()
		if data:
			self.add_line(data)

	# todo use throw an error in Item if match Section.head_pat
	#  using this method to put ^# lines in an item would be confusing.
	#
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

	def set_attrib(self, akey, aval):
		"Set Item attributes given akey and aval"
		self.attribs[akey] = TLAttribute(akey, aval)


	def add_line(self, data):
		"Add a line as either the top task, an attribute, or sub text"
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
		"return true if no header or body, else return false."
		boolean_return_of_Item_is_empty = (not self.top) and (not len(self.subs)) and (not len(self.attribs))
		return boolean_return_of_Item_is_empty

	def is_attrib_only(self):
		"return true if no header or body, else return false."
		boolean_return_of_is_attrib_only = (not self.top) and  (not len(self.subs))
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
	initially named '#In progress' to represet tasks planned for the next day or 
	week, or agile sprint, or whatever period.

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
		return self.get_attrib(Document.dname_attr_str).value

	def _set_doc_name(self, name):
		"setter for doc_name"
		print("called Document _set_doc_name: ", name)
		self.set_attrib(Document.dname_attr_str, name)

	doc_name = property(_get_doc_name, _set_doc_name)

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

			data  = line.rstrip("\n") # todo: fix: stripping newline off blank line makes it not get in body.
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
	def get_attrib(self, key):
		"""
		Return the Document attribute matching key, or None.
		The Document attributes are the attributes of the first Section (index 0)
		on the journal, only if that Section has no text in its 'header' member
		"""
		if len(self.journal[0].header) == 0:
			return self.journal[0].get_attrib(key)
		else:
			return None

	def set_attrib(self, akey, aval):
		"Set Document attributes by putting them in an otherwise empty first Section in the journal"
		# if self.journal[0].is_empty():
		if self.journal[0].is_attrib_section():
		# Document set_attrib calling Section Set Attrib
			self.journal[0].set_attrib(akey, aval )  
		else:
			s = Section()
			s.set_attrib(akey, aval)
			self.journal.insert(0, s)
		# Test this.  It looks like if I add multiple atributes, 
		# each one is in its own section object.

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

	def backlog_str(self):
		"Retun the backlog section as a string"	
		return str(self.backlog)

	def __str__(self):
		#s = "Document: " + str(self.name) + "\n"
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
			self.in_progres = journal_section
			self.journal.remove(journal_section)
		else:	
			self.in_progress.add_line(in_prog_head)

		for section in self.journal:
			for item in section.update_progress():
				self.in_progress.add_item(item)

	def get_day_document(new_tasks_per_day):
		"""create day_document as inprogress + pop some tasks of backlog."""
		d_doc = Document()
		# make_in_progress can be called even if it has already been called.
		self.make_in_progress
		# add in_progress to d_doc
		# need to fundame ally change task update methodology to be in the 
		#	latest curent day file
		#	and the (latest) journal.

def	debExit(message = ""):
	"This func just gets temporarily inserted for top down re checking of main()"
	print("EARLY DEBUG exit(): " + message)
	exit()


def main():
	print("Model classes for tlog.py")

if __name__ == '__main__':
	main()
