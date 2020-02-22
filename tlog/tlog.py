#!/usr/local/bin/python3
"""
First, read and classify each input line as one or more of:
 - a mark down heading for a new Section
 - a task line to create a new Item to add to the list under the 
   current Section
 - text to put under the current Item
 - a "do" task Item to be put in the backlog Section
Then Print out the list of Sections in order with the 
backlog Section at the end 

See tlmodel module journal_documentation for patterns that classify input
lines
"""
from tlmodel import Document  # import re
from tlmodel import TLogInternalException
import fileinput
import journaldir
import sys

# import markdown # avoid html support and coupling to markdon for now

journal_document = Document()
journal_document.doc_name = journaldir.cday_fname

prev_line_blank = False


def sj_file_list_by_dir(latest_dir, history_months):
	"""
	get group of story files and latest journal file name lists given dir
	if none are found in the latest_dir, search back up to history_months
	until at least 1 file is found.
	"""
	file_count = 0
	dirs_to_search = history_months
	search_dir = latest_dir
	while file_count == 0 and dirs_to_search > 0:
		file_count = 0
		sfl = journaldir.get_file_names_by_pattern(
			search_dir, journaldir.story_pat)
		jfl = journaldir.get_file_names_by_pattern(
			search_dir, journaldir.journal_pat)
		file_count = len(sfl) + len(jfl)
		print("{} stories and {} journals in {}".
			  format(len(sfl), len(jfl), search_dir))
		search_dir = journaldir.get_prior_dir(search_dir)
		# print("next search_dir is: {}".format(search_dir))
		if not search_dir:
			dirs_to_search = 0
		else:
			dirs_to_search -= 1
		print("next search_dir is {}.  remaining dirs: {}".
			  format(search_dir, dirs_to_search))

	jfl = jfl[-1:]
	return sfl, jfl


# new_work_section = tlmodel.Section("#" + journaldir.domth )

supported_commands = ["jdir"]
"""
jdir - treat the next argment to tlog as the journal_dir.
"""
my_journal_dir = journaldir.journal_dir
look_back_months = 24
if len(sys.argv) < 2:
	journaldir.init(my_journal_dir)
	s_file_list, j_file_list = sj_file_list_by_dir(my_journal_dir, look_back_months)
	print("no argument sfile_list, jfile_list:", s_file_list, j_file_list)
else:
	if sys.argv[1] in supported_commands:
		tlog_command = sys.argv[1]
		if tlog_command == "jdir":
			# should treat the jdir as the journal dir: stories and a journal
			my_journal_dir = sys.argv[2]
			s_file_list, j_file_list = sj_file_list_by_dir(my_journal_dir, look_back_months)
			# todo if no files, look in previous journaldir.
			print("jdir argument file_list:", tlog_command, s_file_list, j_file_list)
		else:
			raise TLogInternalException("A supported command has no implementation")
	else:
		s_file_list = sys.argv[1:]
		j_file_list = []
		print("(re) initializing Journal from stories:", s_file_list)

# what file lists am I expecting to be non null here?
# file_list should have stories first and 1 journal at the end
# first phase is just input lines to build Items and Sections 
for in_document_file in s_file_list:
	journal_document.add_lines(fileinput.input(in_document_file))

for in_document_file in j_file_list:
	journal_document.add_lines(fileinput.input(in_document_file))

journal_document.make_in_progress("## " + journaldir.domth)

# print("The out doc:", str(journal_document) + '\n')
# print("journaldir.journal_dir", str(journaldir.journal_dir) )
# print("journal_document.doc_name", str(journal_document.doc_name) )

journaldir.write_dir_file(str(journal_document) + '\n',
						  journaldir.journal_dir, journaldir.cday_fname)

## support a method in Document to:
# create day_document as inprogress + pop 3 off backlog from journal.
# new_tasks_per_day = 3
# journal_document.get_day_document(new_tasks_per_day)

# html = markdown.markdown(journal_document.in_progress_str() + '\n')
# journaldir.write_simple( html,
#	journaldir.journal_dir, "todayfile.html")
