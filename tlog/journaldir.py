#!/usr/local/bin/python3 -d
import sys
#journaldir.py
"""
determine directory for journal files based on curent year and month.
if invoked as script, print it to stdout so a shell alias can cd there.
"""
import datetime
import os
import re
from os import listdir
from os.path import isfile, join

default_path = os.path.expanduser('~') + '/journal'
 
jp = os.getenv('JOURNAL_PATH', default_path )
journal_pat =  re.compile(
	'[Jj]ournal-[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].txt')
story_pat =  re.compile('.*story.txt')


def get_repos():
	"todo I think repos needs to change to endevors here."
	repos_file = os.path.expanduser('~') + "/.tlog/repos"
	with open(repos_file) as f:
		repos = f.read().splitlines() # .filter(re.match'!^#', repos) 
	return repos

def get_file_names_by_pattern(dir_name, a_pattern):
	"""
	Get the file names in a directory that match a compiled regex 
	pattern that are not themselves directories.
	"""
	matching_file_list = []
	for f in listdir(dir_name):
		fqp = join(dir_name, f)
		if isfile(fqp) and a_pattern.match(f):
				matching_file_list.append(fqp)
	return matching_file_list



def get_file_names(dir_name):
	"Get the file names in dir_name that are not directories"

	return_file_list = []
	journal_file_list = []
	for f in listdir(dir_name):
		fqp = join(dir_name, f)
		if isfile(fqp):
			if journal_pat.match(f):
				journal_file_list.append(fqp)
			else:
				return_file_list.append(fqp)
	last_journal = sorted(journal_file_list)[-1]
	# todo can do full list when I am tagging story under task 
	return_file_list.append(last_journal)
	return return_file_list

dtn = datetime.datetime.now()
# see http://strftime.org/
yyyy = dtn.strftime('%Y')
mm = dtn.strftime('%m')

dow = dtn.strftime('%a')
dd = dtn.strftime('%d')
dom = dtn.strftime('%-d')

dayth_dict = {'1' : "st", '2' : "nd", '3' : "rd", '4' : "th", 
	'5' : "th", '6' : "th", '7' : "th", '8' : "th", '9' : "th", '10' : "th",
	'11' : "th", '12' : "th", '13' : "th", '14' : "th", '15' : "th", '16' : "th",
	'17' : "th", '18' : "th", '19' : "th", '20' : "th", '21' : "st", '22' : "nd",
	'23' : "rd", '24' : "th", '25' : "th", '26' : "th", '27' : "th", '28' : "th",
	'29' : "th", '30' : "th", '31' : "st"}

domth = dow + ' ' + dom + dayth_dict[dom]
journal_dir = os.path.join(jp, yyyy, mm) 

cday_fname = 'journal' + '-' + yyyy + '-' + mm + '-' + dd + '.txt'

def path_file_join(p, f):
	"wrapper helps prevent module os from being needed in calling modules."
	return(os.path.join(p , f))

def read_file_str(filepath):
	data = ""
	if os.path.isfile(filepath):
		with open(filepath, 'r') as data_file:
			data = data_file.read()
	return str(data)

def write_dir_file(new_content, dir_name, doc_name):
	filepath = os.path.join(dir_name , doc_name)
	if os.path.isfile(filepath):
		previous_content = read_file_str(filepath)
		if previous_content == new_content:
			print("new content same as old. Nothing written.")
		else:
			print("new content is different than content from old file. renaming")
			# if writing, do this:
			olddir = os.path.join(dir_name , "old")
			if not os.path.isdir(olddir):
				os.makedirs(olddir) 
			os.rename(filepath, os.path.join(olddir, doc_name))
			jfd = open(filepath, "w")
			jfd.write(new_content)
			jfd.close
	else:
		jfd = open(filepath, "w")
		jfd.write(new_content)
		jfd.close

	print("Journal File: " + str(filepath))

def write_simple(new_content, dir_name, doc_name):
	filepath = os.path.join(dir_name , doc_name)
	sfd = open(filepath, "w")
	sfd.write(new_content)
	sfd.close

	print("New File: " + str(filepath))

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1] == "init":
		if not os.path.exists(journal_dir):
			os.makedirs(journal_dir)
	
	print(journal_dir)

	#print(dom + dayth_dict[dom])