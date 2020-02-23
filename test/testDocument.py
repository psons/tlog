#!/usr/local/bin/python3

import unittest
from tlmodel import Document
from tlmodel import TLAttribute
from testtl import doc1_text
from testtl import doc_attrib_line
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
		"Does get_attrib return a name and value for a Document attribute?"
		attrib_l = TLAttribute.fromline(doc_attrib_line)
		attrib_d = Document.fromtext(doc1_text).get_attrib(ad1)
		self.assertEqual(attrib_d.value, attrib_l.value)
		self.assertEqual(attrib_d.name, attrib_l.name)

	def testDocumentSetAttrib(self):
		"Does set_attrib match get_attrib for a name and value for a Document attribute?"
		d1 = Document.fromtext(testDocument.docIn)
		d1.set_attrib(ad1, vd1)
		attr = d1.get_attrib(ad1)
		self.assertEqual(attr.value, vd1)

	# todo modify this test to check for duplicat attribute in the un named section.
	def testDocumentSecondSetAttrib(self):
		"Does set_attrib match get_attrib for a name and value for a Document attribute?"
		d1 = Document.fromtext(testDocument.docIn)
		d1.set_attrib(ad1, vd1)
		d1.set_attrib(ad1, vd2) # set it again
		attr = d1.get_attrib(ad1)
		print("d1 is: ", d1)
		self.assertEqual(attr.value, vd2)

	def testDocumentNameProperty(self):
		"Does assignment to adocument.doc_name work?"
		d1 = Document.fromtext(testDocument.docIn)
		a_doc_name = "Moby Doc.txt"
		d1.doc_name = a_doc_name
		self.assertEqual(d1.doc_name, a_doc_name)


if __name__ == '__main__':
	unittest.main()
