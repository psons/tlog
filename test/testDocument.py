#!/usr/local/bin/python3
import re
import unittest
from tldocument import Document
from tldocument import DocStructure
from docsec import Item
from testtl import doc1_text
from testtl import ad1
from testtl import vd1
from testtl import vd2

class testDocument(unittest.TestCase):
	"Tests for the Documet class."

	docTitle = "A Test Doc"

	docIn = """\
a little preamble text
#Section
x - did somthing
 - sub item list item done
## a section below
text in a section below
/ - item in progress
/ - item with sub in progress
 - sub of the in progress.
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""
	docIn2 = """\
# Sun 21st
x - rest
# Mon 22nd
x - did somthing
 - sub of did somthing
/ - item in progress
/ - item with sub in progress
 - sub of the in progress.
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""
	docOut2 = """\
# Sun 21st
x - rest
# Mon 22nd
x - did somthing
 - sub of did somthing
/ - item in progress
/ - item with sub in progress
 - sub of the in progress.
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""
	journalOut = """\
a little preamble text
#Section
x - did somthing
 - sub item list item done
## a section below
text in a section below
/ - item in progress
/ - item with sub in progress
 - sub of the in progress.\
"""
	backlogOut = """\
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""

	#docOut = "Document: " + docTitle + "\n" + journalOut + "\n" + backlogOut
	docOut =  journalOut + "\n" + backlogOut

	journalProgressOut = """\
a little preamble text
#Section
x - did somthing
 - sub item list item done
## a section below
text in a section below
u - item in progress
u - item with sub in progress
 - sub of the in progress.\
"""

	inProgressOut = Document.defautInProgHead + "\n" + """\
/ - item in progress
/ - item with sub in progress
 - sub of the in progress.\
"""

	docInProgressOut = "\n".join( [ journalProgressOut, inProgressOut,
									backlogOut])

	small_story = """\
maxTasks: 3
d - start on the small story
d - some more work on the small story
d - refine the small story work
d - finish the small story!\
	"""

	small_story_3_tasks = """\
	d - start on the small story
	d - some more work on the small story
	d - refine the small story work\
	"""

	def testDocumentJournal(self):
		text_lines = testDocument.docIn.split("\n")
		dtest  = Document(testDocument.docTitle, text_lines)
		#print("str(dtest):" + str(dtest))
		self.assertEqual(dtest.journal_str(), testDocument.journalOut)

	def testDocumentBacklog(self):
		text_lines = testDocument.docIn.split("\n")
		dtest = Document(testDocument.docTitle, text_lines)
		self.assertEqual(testDocument.backlogOut, dtest.backlog_str())

	def testDocumentWhole(self):
		"Lines from docIn should match str() of Document made from them."
		text_lines = testDocument.docIn.split("\n")
		dtest  = Document(testDocument.docTitle, text_lines)
		self.assertEqual(str(dtest), testDocument.docOut)

	def testDocumentJournalProgress(self):
		"Journal after make_in_progress() called.  Has items marked unfinished"
		text_lines = testDocument.docIn.split("\n")
		dtest  = Document(testDocument.docTitle, text_lines)
		dtest.make_in_progress()
		self.assertEqual(dtest.journal_str(), testDocument.journalProgressOut)

	def testDocumentInProgress(self):
		"In progress section after make_in_progress() called"
		text_lines = testDocument.docIn.split("\n")
		dtest  = Document(testDocument.docTitle, text_lines)
		dtest.make_in_progress()
		self.assertEqual(testDocument.inProgressOut, dtest.in_progress_str())

# add test for scenarios where the in progress section is existing,
# especially with some completed tasks, that must not get lost!

	def testDocumentExistingProgressSection(self):
		"Re use In progress section for make_in_progress()"
		text_lines = testDocument.docIn2.split("\n")
		dtest  = Document(testDocument.docTitle, text_lines)
		dtest.make_in_progress("# Mon 22nd")
		self.assertEqual(str(dtest), testDocument.docOut2)

	def testDocumentWholeInProgres(self):
		"Whole document after make_in_progress() called"
		text_lines = testDocument.docIn.split("\n")
		dtest  = Document(testDocument.docTitle, text_lines)
		dtest.make_in_progress()
		self.assertEqual(str(dtest), testDocument.docInProgressOut)

	def testDocumentWhole2(self):
		inDoc2  = """\
journal-2016-05-08.txt

x - save taxes to windows PC
x - save taxes as encrypted 7zip to fireproof box
d - put way misc paper tax files
/ - do the roll day story in tlog/backlog/Roll Day story.txt\
"""
		outDoc2 =  """\
journal-2016-05-08.txt

x - save taxes to windows PC
x - save taxes as encrypted 7zip to fireproof box
/ - do the roll day story in tlog/backlog/Roll Day story.txt
d - put way misc paper tax files\
"""
		text_lines = inDoc2.split("\n")
		dtest  = Document(testDocument.docTitle, text_lines)
		#print("testDocumentWhole2 str(dtest):" + str(dtest))
		self.assertEqual(str(dtest), outDoc2)

	#@unittest.skip("Document attribute screwing this up. ")
	def testDocumentWhole3(self):
		self.assertEqual(str(Document.fromtext(doc1_text)), doc1_text)

	def testDocumentGetAttrib(self):
		"Does get_doc_attrib return a value for a Document attribute?"
		val = Document.fromtext(doc1_text).get_doc_attrib(ad1)
		self.assertEqual(vd1, val)


	def testDocumentSetAttrib(self):
		"Does set_doc_attrib match get_doc_attrib for a name and value for a Document attribute?"
		d1 = Document.fromtext(testDocument.docIn)
		d1.set_doc_attrib(ad1, vd1)
		attr = d1.get_doc_attrib(ad1)
		self.assertEqual(vd1, attr)

	# todo modify this test to check for duplicat attribute in the un named section.
	def testDocumentSecondSetAttrib(self):
		"Does set_doc_attrib match get_doc_attrib for a name and value for a Document attribute?"
		d1 = Document.fromtext(testDocument.docIn)
		d1.set_doc_attrib(ad1, vd1)
		d1.set_doc_attrib(ad1, vd2) # set it again
		attr = d1.get_doc_attrib(ad1)
		#print("d1 is: ", d1)
		self.assertEqual(vd2, attr)

	def testDocumentNameProperty(self):
		"Does assignment to adocument.doc_name work?"
		d1 = Document.fromtext(testDocument.docIn)
		a_doc_name = "Moby Doc.txt"
		d1.doc_name = a_doc_name
		self.assertEqual(d1.doc_name, a_doc_name)

	def testDocumentMaxTasks(self):
		small_story_doc = Document.fromtext(testDocument.small_story)
		mt = small_story_doc.max_tasks
		task_list = small_story_doc.get_backlog_list(mt)
		self.assertEqual(int(mt), len(task_list))

class special_sections:
	"holds some test data for DocumentStructure"
	def __init__(self):
		self.ds = DocStructure('^#')
		self.a_pat = re.compile('^[aA] *-')
		self.x_pat = re.compile('^[xX] *-')
		self.ds.add_leader_entry('# Past Tasks', [self.a_pat, self.x_pat])
		self.ds.add_leader_entry('# Current Tasks', ['^[dD] *-'])
		self.test_line = 'x - is a completed task'
		self.test_item = Item().fromtext(self.test_line)
		# print(str(self.ds) + "\n")
		# place_to_put = special_sections.insert_item("")

class testDocumentStructure(unittest.TestCase):

	def testDocumentStructure(self):
		"""
		show that leader lookups from the same add_leader_entry refer to
		 the same instance object
		"""
		test_data_o = special_sections()
		test_data_o.ds.insert_item(test_data_o.test_item)
		self.assertIs(test_data_o.ds.leader_instance_dict[test_data_o.x_pat],
					  test_data_o.ds.insert_item(test_data_o.test_item))


	def testGetSection(self):
		"""
		get a section that matches some text
		"""
		ss = special_sections()
		self.assertIs(ss.ds.leader_instance_dict[ss.a_pat], ss.ds.leader_instance_dict[ss.x_pat])


if __name__ == '__main__':
	unittest.main()
