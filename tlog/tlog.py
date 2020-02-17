#!/usr/local/bin/python3
"""
First, read and classify each input line as one or more of:
 - a mark down headding for a new Section
 - a task line to create a new Item to add to the list under the 
   curent Section
 - text to put under the curent Item
 - a "do" task Item to be put in the backlog Section
Then Print out the list of Sections in order with the 
backlog Section at the end 

See tlmodel module journal_documentation for patterns that classify input
lines
"""
from tlmodel import Document  #import re
from tlmodel import TLogInternalException
import fileinput
import journaldir
import sys
#import markdown # avoid html support and coupling to markdon for now

journal_document = Document()
journal_document.doc_name = journaldir.cday_fname

prev_line_blank = False

def sj_file_list_by_dir(dir):
	"get story and journal file name lists given dir"
	sfl = journaldir.get_file_names_by_pattern(
				journaldir.journal_dir, journaldir.story_pat)	
	jfl = journaldir.get_file_names_by_pattern(
			journaldir.journal_dir, journaldir.journal_pat)
	jfl =  jfl[-1:]
	return sfl, jfl

#new_work_section = tlmodel.Section("#" + journaldir.domth )

supported_commands = ["jdir"]
"""
jdir - treat the next argment to tlog as the journal_dir.
"""
if len(sys.argv) < 2:
	s_file_list, j_file_list = sj_file_list_by_dir(journaldir.journal_dir)
	print("no argument sfile_list, jfile_list:", s_file_list, j_file_list )
else:
	if sys.argv[1] in supported_commands:
		tlog_command = sys.argv[1]
		if tlog_command  == "jdir" :
			# should treat the jdir as the journal dir: stories and a journal
			journaldir.journal_dir = sys.argv[2]
			s_file_list, j_file_list = sj_file_list_by_dir(journaldir.journal_dir)
			print("jdir argument file_list:", tlog_command, s_file_list, j_file_list )
		else:
			raise TLogInternalException("A supported command has no implementation")
	else:
		s_file_list = sys.argv[1:]
		j_file_list = []
		print("(re) initializing Journal from stories:", s_file_list )		

# what file lists am I expecting to be non null here?
# file_list should have stories first and 1 journal at the end
# first phase is just input lines to build Items and Sections 
for in_document_file in s_file_list:
	journal_document.add_lines(fileinput.input(in_document_file))

for in_document_file in j_file_list:
	journal_document.add_lines(fileinput.input(in_document_file))

journal_document.make_in_progress("## " + journaldir.domth)

# print("The out doc:", str(journal_document) + '\n')
#print("journaldir.journal_dir", str(journaldir.journal_dir) )
#print("journal_document.doc_name", str(journal_document.doc_name) )

journaldir.write_dir_file(str(journal_document) + '\n', 
	journaldir.journal_dir, journal_document.doc_name)

## support a method in Document to:
# create day_document as inprogress + pop 3 of backlog from journal.
new_tasks_per_day = 3
journal_document.get_day_document(new_tasks_per_day)

#html = markdown.markdown(journal_document.in_progress_str() + '\n')
#journaldir.write_simple( html,
#	journaldir.journal_dir, "todayfile.html")
