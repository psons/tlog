#!/usr/local/bin/python3
"""
2020-03-06: Evolving toward a memory data structure built of collections of Document
Objects.  Stories read from Endeavor files, for example.

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

# import markdown # avoid html support and coupling to markdown for now

my_journal_dir = journaldir.journal_dir

user_paths = journaldir.UserPaths()

journal_document = Document()
journal_document.doc_name = journaldir.cday_fname

story_task_document = Document()
story_task_document.doc_name = "Story tasks from" + user_paths.endeavor_file

prev_line_blank = False


def sj_file_list_by_dir(latest_dir, history_months):
	"""
	get group of story files and latest journal file name lists given dir
	if none are found in the latest_dir, search back up to history_months
	until at least 1 file is found.
	:param latest_dir: current journaldir to look back in history from to fine files.
	:param history_months: limit on how far back to search
	:return: list of story files, list of journal files, and the dir they were found.
	"""
	file_count = 0
	dirs_to_search = history_months
	next_search_dir = latest_dir
	while file_count == 0 and dirs_to_search > 0:
		search_dir = next_search_dir
		sfl = journaldir.get_file_names_by_pattern(
			search_dir, journaldir.story_pat)
		jfl = journaldir.get_file_names_by_pattern(
			search_dir, journaldir.journal_pat)
		file_count = len(sfl) + len(jfl)
		print("{} stories and {} journals in {}".
			  format(len(sfl), len(jfl), search_dir))
		next_search_dir = journaldir.get_prior_dir(search_dir) # can return None
		if not next_search_dir:
			dirs_to_search = 0 # loop to end if no sensible search_dir
		else:
			dirs_to_search -= 1

	jfl = jfl[-1:] # just the last journal file in the list
	return sfl, jfl, search_dir

def load_doc_from_file(file_name):
	file_text = journaldir.read_file_str(file_name)
	return Document.fromtext(file_text)

def shorten_stories(long_story_doc_list):
	short_s_doc_list = [Document.fromtext(str(doc)) for doc in long_story_doc_list]
	return [doc.shorten_backlog() for doc in short_s_doc_list]

supported_commands = ["jdir"]
"""
jdir - treat the next argment to tlog as the journal_dir.
"""

look_back_months = 24
if len(sys.argv) < 2:
	journaldir.init(my_journal_dir)
	s_file_list, j_file_list, prev_journal_dir = sj_file_list_by_dir(my_journal_dir, look_back_months)
	print("no argument sfile_list, jfile_list:", s_file_list, j_file_list)
else:
	if sys.argv[1] in supported_commands:
		tlog_command = sys.argv[1]
		if tlog_command == "jdir":
			my_journal_dir = sys.argv[2]
			s_file_list, j_file_list, prev_journal_dir = sj_file_list_by_dir(my_journal_dir, look_back_months)
			print("jdir argument file_list:", tlog_command, s_file_list, j_file_list)
		else:
			raise TLogInternalException("A supported command has no implementation")
	else:
		s_file_list = sys.argv[1:]
		j_file_list = []
		print("(re) initializing Journal from stories:", s_file_list)

journal_story_doc_list = [load_doc_from_file(js_file) for js_file in s_file_list]
short_j_story_doc_list = shorten_stories(journal_story_doc_list)

# More advanced versions of endeavor file format later.
# should treat the jdir as the journal dir: stories and a journal
endeavor_list = journaldir.load_endeavors(user_paths)
# print("endeavor_list: \n", " \n ".join([str(e) for e in endeavor_list]),)
endeavor_story_doc_list = [load_doc_from_file(es_file) for e_list in endeavor_list for es_file in e_list.story_list]
short_e_story_doc_list = shorten_stories(endeavor_story_doc_list)

short_s_doc_list = short_j_story_doc_list + short_e_story_doc_list
for short_story_doc in short_s_doc_list:
	story_task_document.merge_backlog(short_story_doc.backlog)

story_task_document.generate_backlog_title_hashes()

for in_document_file in j_file_list:
	journal_document.add_lines(fileinput.input(in_document_file))

journal_document.make_in_progress("## " + journaldir.domth)
journal_document.merge_backlog(story_task_document.backlog)

journal_document.doc_name=journaldir.cday_fname
if my_journal_dir != prev_journal_dir:
	print("Wil drop journal because it is from a back month")
	journal_document.drop_journal()

journaldir.write_dir_file(str(journal_document) + '\n',
						  journaldir.journal_dir, journal_document.doc_name)

## support a method in Document to:
# create day_document as inprogress + pop 3 off backlog from journal.
# new_tasks_per_day = 3
# journal_document.get_day_document(new_tasks_per_day)

# html = markdown.markdown(journal_document.in_progress_str() + '\n')
# journaldir.write_simple( html,
#	journaldir.journal_dir, "todayfile.html")
