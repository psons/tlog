#!/usr/local/bin/python3

"""
Improved testing methodology:
As I add features, I need to add them to common document that are 
used for all tests so that I dont have to remember to update methods
like deep copy when I add attribute support.  Updating the test 
input should break tests for things that do not support the new 
input.
"""
import base64
import unittest
from tlmodel import Item
from tlmodel import Section
from tlmodel import TLAttribute

ad1 = "aDocAttribute"
vd1 = " TheDocValue"
vd2 = " TheChangedDocValue"
doc_attrib_line = ad1 + ':' + vd1


header_line = "# The Header"
as1 = "aSectionAttribute"
vs1 = " TheSectionValue"
as2 = "aNewSectionAttribute"
vs2 = " TheNewSectionValue"

section_attrib_line = as1 + ':' + vs1
xtask_line = "x - completed task"
xtask_sub_line = " - sub of completed task"
second_header_line = "## a second section"
inprog_task_line = " - sub of in progress task"

ai1 = "anItemAttribute"
vi1 = " TheItemValue"
item_attrib_line1 = ai1 + ':' + vi1

ai2 = "anotherItemAttribute"
vi2 = " AnotherItemValue"
item_attrib_line2 = ai2 + ':' + vi2

item_2attr_str = "\n".join([item_attrib_line1, item_attrib_line2])

dtask_line = "d - do task"
dtask_sub1_line = " - sub item list item 1"
dtask_sub2_line = " - sub item list item 2"
dtask_text_line = "free text"

# this gets computed in a test and is needed as an expected value
#dtask_saved_hash = "titleHash:9b35f4f8b4573f2c8239f0c49463f04f"
dtask_saved_hash = "titleHash:9b35f4f8b4"

dtask_item_text = "\n".join([dtask_line, item_attrib_line1, 
	dtask_sub1_line, dtask_sub2_line, dtask_text_line])

dtask_item_text_w_saved_hash = "\n".join([dtask_line, item_attrib_line1,
	dtask_saved_hash,
	dtask_sub1_line, dtask_sub2_line, dtask_text_line])

dtask_line_modified = "d - do task changed"
dtask_item_text_w_saved_hash_modified_title = "\n".join([dtask_line_modified,
	item_attrib_line1, dtask_saved_hash,
	dtask_sub1_line, dtask_sub2_line, dtask_text_line])

doc1_text = "\n".join( [doc_attrib_line, header_line, section_attrib_line,
	xtask_line, xtask_sub_line, 
	second_header_line, inprog_task_line,
	dtask_line,dtask_sub1_line, dtask_sub2_line, dtask_text_line]
	)

dtask2_line = "d - do another task"
dtask2_sub1_line = " - sub of do another"

sec_two_items = "\n".join([dtask_line, dtask2_sub1_line, dtask2_line, dtask2_sub1_line ])
sec_attrib_wrong = "\n".join([header_line, xtask_line, section_attrib_line])
sec_w_attrib = "\n".join([section_attrib_line, header_line])

sec_head = """\
#Section\
"""
sec_item = """\
d - do something\
"""
sec_head_item = """\
#Section
d - do something\
"""
sec_attr_item = """\
DocName:journal-2020-02-22.md
d - do something\
"""
sec_attr1 = """\
DocName:journal-2020-02-22.md\
"""
sec_attr2 = """\
DocName:journal-2020-02-22.md

\
"""
sec_empty = """\


\
"""
is_attrib_section_casaes = [
	(sec_head, False),
	(sec_item, False),
	(sec_head_item, False),
	(sec_attr_item, False),
	(sec_attr1, True),
	(sec_attr2, False),
	(sec_empty, False)
]

class TestItem(unittest.TestCase):

	def testNoneNull(self):
		self.assertEqual(str(Item(None)), "")

	def testEmptyItemTrue(self):
		self.assertTrue(Item().is_empty())

	def testEmptyTopItemFalse(self):
		self.assertFalse(Item("d - somthing").is_empty())

	def testEmptySubItemFalse(self):
		self.assertFalse(Item(" - sub line").is_empty())

	def testEmptyAttribItemFalse(self):
		self.assertFalse(Item("a: v").is_empty())

	def testSubItem(self):
		"Item with just sub text look ok?"
		txt = "free text"
		itest = Item(txt)
		self.assertEqual(str(itest), txt)

	def testItemWithList(self):
		out = """\
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""
		itest = Item("d - do somthing")
		itest.add_line(" - sub item list item 1")
		itest.add_line(" - sub item list item 2")
		itest.add_line("free text")
		self.assertEqual(str(itest), out)

	def testFullBlownItem(self):
		"A full blown item can be created from text and converted back to the same string."
		itest = Item.fromtext(dtask_item_text)
		self.assertEqual(str(itest), dtask_item_text)


	def testItemDeepCopyDifferentObject(self):
		"Does item.deep_copy() return an item with a different id?"
		itest = Item("d - do somthing")
		itest1 = itest.deep_copy()
		self.assertNotEqual(id(itest), id(itest1))

	def testItemDeepCopyEqual(self):
		"Does item.deep_copy() return a same string item?"
		itest = Item.fromtext(dtask_item_text)
		itest1 = itest.deep_copy()
		self.assertEqual(str(itest), str(itest1))

	def testGetItemTitle1(self):
		"""get_title() base case with leader and title"""
		leader = "d -"
		title_in = "item with no sub lines!"
		itest = Item("{}{}".format(leader, title_in))
		title_out = itest.get_title()
		# print("x{}x".format(itest.top))
		# print("title_in:{} title_out:{}".format(title_in, title_out))
		self.assertEqual(title_in, title_out)

	def testGetItemTitle2(self):
		"""get_title() with trailing whitespace to ignore in title"""
		leader = "d -"
		title_in = "item with no sub lines!"
		itest = Item("{} {} ".format(leader, title_in)) # trailing white space
		title_out = itest.get_title()
		# print("x{}x".format(itest.top))
		# print("title_in:{} title_out:{}".format(title_in, title_out))
		self.assertEqual(title_in, title_out)

	def testGetItemTitle3(self):
		"""get_title() with leading white space to ignore in title"""
		leader = "d -"
		title_in = "item with no sub lines!"
		itest = Item("{} {} ".format(leader, title_in)) # leading white space
		title_out = itest.get_title()
		# print("x{}x".format(itest.top))
		# print("title_in:{} title_out:{}".format(title_in, title_out))
		self.assertEqual(title_in, title_out)

	def testGetItemTitle4(self):
		"""get_title() with only white space in title"""
		leader = "d -"
		title_in = ""
		expected = None
		itest = Item("{}{} ".format(leader, title_in))
		title_out = itest.get_title()
		# print("x{}x".format(itest.top))
		# print("title_in:{} title_out:{} expected:{}".format(
		# 	title_in, title_out, expected))
		self.assertEqual(expected, title_out)

	def testGetItemTitleHash1(self):
		"""Base case"""
		leader = "d -"
		title_in = "item with no sub lines!"
		itest = Item("{} {} ".format(leader, title_in)) # leading white space
		t_hash = itest.get_title_hash()
		self.assertEqual(t_hash, 'f3ebd9014f')

	def testGetItemTitleHash2(self):
		"""empty title should return empty string for hash"""
		leader = "d -"
		title_in = ""
		itest = Item("{} {} ".format(leader, title_in)) # leading white space
		t_hash = itest.get_title_hash()
		self.assertEqual('', t_hash)

	def testSaveItemTitleHash1(self):
		"""Saved title hash matches expected"""
		itest = Item.fromtext(dtask_item_text)
		itest.save_title_hash()
		saved_hash = itest.get_saved_title_hash()
		#print("itest:\n", itest)
		#print("dtask_item_text_w_saved_hash:" + dtask_item_text_w_saved_hash)
		self.assertEqual('9b35f4f8b4', saved_hash)

	def testSaveItemModifiedTitleHash1(self):
		"""
		Saved title hash with modified title is detectable
		Simulates detection of when a user has modified a task title that came in
		from a story file
		"""
		itest = Item.fromtext(dtask_item_text_w_saved_hash_modified_title)
		# hash is in the saved input
		#print("itest:\n", itest)
		#print("dtask_item_text_w_saved_hash (unmodified) :" + dtask_item_text_w_saved_hash)
		# todo fix test
		self.assertEqual(False, itest.title_matches_hash())

	def testSaveItemUnModifiedTitleHash1(self):
		"""
		Saved title hash with modified title is detectable
		Simulates detection of when a user has modified a task title that came in
		from a story file
		"""
		itest = Item.fromtext(dtask_item_text_w_saved_hash)
		# hash is in the saved input
		# print(itest.get_title_hash())
		# print("itest:\n", itest)
		# print("dtask_item_text_w_saved_hash (unmodified) :\n" + dtask_item_text_w_saved_hash)
		self.assertEqual(True, itest.title_matches_hash())

	def testItemNoSub(self):
		out = "d - item with no sub lines!"
		itest = Item(out)
		self.assertEqual(str(itest), out)

	def testItemNoHeader(self):
		out = " - subitem with no item header"
		itest = Item(None)
		itest.subs.append(out)
		self.assertEqual(str(itest), out)

	def testinProgressPatternSlash(self):
		data = "/ - doing somthing"
		self.assertTrue(Item.in_progress_pat.match(data))

	def testinProgressPatternBackSlash(self):
		data = "\ - doing somthing else"
		self.assertTrue(Item.in_progress_pat.match(data))

	def testChange_in_prog_2_unfin(self):
		data = "\ - doing somthing else"
		itest = Item(data)
		itest.in_prog_2_unfin()
		self.assertTrue(Item.unfinished_pat.match(itest.top))

	def testItemSetAttribGetAttribSymmetry(self):
		"""Item get_item_attrib / set_doc_attrib symmetry"""
		itest = Item()
		itest.set_attrib(ai1, vi1)
		self.assertEqual(str(itest.get_item_attrib(ai1)), vi1)


	def testItemGetAttribNone1(self):
		"""Item get_item_attrib should return None of the key is not present"""
		itest = Item()
		self.assertEqual(itest.get_item_attrib(ai1), None)


	def testItemGetAttribNone2(self):
		"""Item get_item_attrib should return None of the key is not present"""
		itest = Item(dtask_line)
		self.assertEqual(itest.get_item_attrib(ai1), None)

	def testItemAttrib(self):
		itest = Item(item_attrib_line1)
		self.assertEqual(str(itest.get_item_attrib(ai1)), vi1)

	def testItem2Attribs(self):
		itest = Item(item_attrib_line1)
		itest.add_line(item_attrib_line2)
		self.assertEqual(str(itest.get_item_attrib(ai1)), vi1)
		self.assertEqual(str(itest.get_item_attrib(ai2)), vi2)

	def testItem2AttribsStr(self):
		"Does attribs_str work for a 2 attribute Item?"
		itest = Item(item_attrib_line1)
		itest.add_line(item_attrib_line2)
		#print(itest.attribs_str())
		self.assertEqual(item_2attr_str, itest.attribs_str())


class testSection(unittest.TestCase):

	def testEmptySectionTrue(self):
		"Does the is_empty() return true for empty section?"
		self.assertTrue(Section().is_empty())

	def testEmptySectionHeaderFalse(self):
		"Does the is_empty() return false for section with a heading?"
		self.assertFalse(Section("# header").is_empty())

	def testEmptySectionItemFalse(self):	
		"Does the is_empty() return false for section with an item with a top?"
		self.assertFalse(Section("d - task").is_empty())

	def testEmptySectionItemSubFalse(self):	
		"Does the is_empty() return false for section with an item with a sub text?"
		self.assertFalse(Section(" - task detail").is_empty())

	def testSectionWithItem(self):
		out = """\
#Section
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""
		stest = Section("#Section")
		stest.add_line("d - do somthing")
		stest.add_line(" - sub item list item 1")
		stest.add_line(" - sub item list item 2")
		stest.add_line("free text")
		self.assertEqual(out, str(stest))

	def testStrItemsList(self):
		out = """\
d - do 1
d - do 2
d - do 3\
"""
		stest = Section("d - do 1")
		stest.add_line("d - do 2")
		stest.add_line("d - do 3")
		self.assertEqual(out, stest.str_body())

	def testStrItemsHead(self):
		out = """\
#  a Header\
"""
		stest = Section("#  a Header")
		self.assertEqual(stest.str_body(), "")


	def testStrItemsAttribute(self):
		out = """\
#  a Header
AnAttributeName: the Attribute Value\
"""
		stest = Section("#  a Header")
		stest.add_line("AnAttributeName: the Attribute Value")
		self.assertEqual(str(stest), out)

	#@unittest.skip("Reworking  testing with a better way to initialize multi line things.")
	def testSectionGetAttributeNone(self):
		"Does Section get_attribute return None if the first Item has a top?"
		stest = Section.fromtext(sec_attrib_wrong)
		self.assertEqual(stest.get_section_attrib(as1), None)

	def testSectionGetAttribute(self):
		"Does Section get_attribute return the attribute?"
		stest = Section.fromtext(sec_w_attrib)
		self.assertEqual(vs1, stest.get_section_attrib(as1))

	def testSectionSetAttributeNew(self):
		"Does set_attribute add a new attribute"
		stest = Section()
		stest.set_sec_attrib(as1, vs1)
		self.assertEqual(vs1, stest.get_section_attrib(as1))
 
	def testSectionSetAttributeReplace(self):
		"Does set_attribute update an existing attribute?"
		stest = Section.fromtext(sec_w_attrib)
		stest.set_sec_attrib(as1, vs2)
		self.assertEqual(vs2, stest.get_section_attrib(as1))

	def testSectionSetAttributeAdd(self):
		"""
		Does set_attribute add an attribute if a different one 
		already exists?
		"""
		stest = Section.fromtext(sec_w_attrib)
		stest.set_sec_attrib(as2, vs2)
		self.assertEqual(vs2, stest.get_section_attrib(as2))

	def testSectionSetAttributeWithItem(self):
		"""
		Does set_attribute add an attribute if there are Items in the Section? 
		"""
		stest = Section.fromtext(sec_two_items)
		stest.set_sec_attrib(as2, vs2)
		self.assertEqual(vs2, stest.get_section_attrib(as2))


	def testSectionGetAttributeNotFound(self):
		"Does Section get_attribute for a key that is not present return None?"
		stest = Section.fromtext(sec_w_attrib)
		self.assertIs(stest.get_section_attrib("wrongKey"), None)

	def testSectionWith2Items(self):
		stest = Section.fromtext(sec_two_items)
		self.assertEqual(sec_two_items, str(stest))

	def testSectionWithNoBody(self):
		out = """\
#Section with no body_items\
"""
		stest = Section("#Section with no body_items")
		self.assertEqual(str(stest), out)

	def testSectionInProgItem(self):
		out = """\
\ - doing somthing else\
"""
		stest = Section("\ - doing somthing else")
		self.assertEqual(str(stest), out)

	def testUpdateProgress1(self):
		"test marking in progress as unfinished for \ - "
		data = "\ - one thing going on"
		out = "u - one thing going on"
		itest = Item(data)
		itest.in_prog_2_unfin()
		self.assertEqual(str(itest), out) 

	def testUpdateProgress2(self):
		"test marking in progress as unfinished for / - "
		data = "/ - another thing going on"
		out = "u - another thing going on"
		itest = Item(data)
		itest.in_prog_2_unfin()
		self.assertEqual(str(itest), out) 

	def test_is_attrib_section(self):
		"Does the is_empty() return false for section with an item with a sub text?"
		for case in is_attrib_section_casaes:
			input_val = case[0]
			expected = case[1]
			actual = Section.fromtext(input_val).is_attrib_section()
			#print("input: {} expected: {}, actual: {}".format(input_val, expected, actual))
			self.assertEqual(expected, actual)

class testTLAttribute(unittest.TestCase):
	positive_key = "SomeAttribute" 
	positive_value = " the value of it"
	valid_line = positive_key + ":" + positive_value

	def positive_pattern():
		return TLAttribute.attr_pat.match(testTLAttribute.valid_line)


	def negitive_pattern():
		data = "SomeAttribute the value of it"
		return TLAttribute.attr_pat.match(data)


	def testTLAttributePatternMatch(self):
		"Does the recognition pattern return a match object?"
		self.assertTrue(testTLAttribute.positive_pattern())


	def testTLAttributePatternNoMatch(self):
		"Does a pattern mismatch return None?"
		self.assertFalse(testTLAttribute.negitive_pattern())
		
	def testTLAttributePatternKey(self):
		"Does a pattern match set the key?"

		mo = testTLAttribute.positive_pattern() # mo is match Object
		testAttr = TLAttribute(mo.group(1), mo.group(2))

		self.assertEqual(testAttr.name, testTLAttribute.positive_key)
		self.assertEqual(testAttr.value, testTLAttribute.positive_value)

	def testTLAttributeStr(self):
		"str() of a TLAttribute should give the text it was made from"
		self.assertEqual(
			str(TLAttribute.fromline(testTLAttribute.valid_line)), 
			testTLAttribute.valid_line)


if __name__ == '__main__':
	#print(doc1_text)
	unittest.main()

