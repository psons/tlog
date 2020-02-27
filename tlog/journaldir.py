#!/usr/local/bin/python3 -d
import sys

# journaldir.py
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

journal_path = os.getenv('JOURNAL_PATH', default_path)
journal_pat = re.compile(
	'[Jj]ournal-[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].md')
story_pat = re.compile('.*story.md')


def get_repos():
	"""todo I think repos needs to change to endevors here."""
	repos_file = os.path.expanduser('~') + "/.tlog/repos"
	with open(repos_file) as f:
		repos = f.read().splitlines()  # .filter(re.match'!^#', repos)
	return repos


def get_file_names_by_pattern(dir_name, a_pattern):
	"""
	Get the file names in a directory that match a compiled regex 
	pattern that are not themselves directories.
	"""
	matching_file_list = []
	if not os.path.isdir(dir_name):
		return matching_file_list

	for f in sorted(listdir(dir_name)):
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

dayth_dict = {'1': "st", '2': "nd", '3': "rd", '4': "th",
			  '5': "th", '6': "th", '7': "th", '8': "th", '9': "th", '10': "th",
			  '11': "th", '12': "th", '13': "th", '14': "th", '15': "th", '16': "th",
			  '17': "th", '18': "th", '19': "th", '20': "th", '21': "st", '22': "nd",
			  '23': "rd", '24': "th", '25': "th", '26': "th", '27': "th", '28': "th",
			  '29': "th", '30': "th", '31': "st"}

domth = dow + ' ' + dom + dayth_dict[dom]
journal_dir = os.path.join(journal_path, yyyy, mm)

cday_fname = 'journal' + '-' + yyyy + '-' + mm + '-' + dd + '.md'


def path_file_join(p, f):
	"wrapper helps prevent module os from being needed in calling modules."
	return (os.path.join(p, f))


def read_file_str(filepath):
	data = ""
	if os.path.isfile(filepath):
		with open(filepath, 'r') as data_file:
			data = data_file.read()
	return str(data)


def write_dir_file(new_content, dir_name, doc_name):
	filepath = os.path.join(dir_name, doc_name)
	if os.path.isfile(filepath):
		previous_content = read_file_str(filepath)
		if previous_content == new_content:
			print("new content same as old. Nothing written.")
		else:
			print("new content is different than content from old file. renaming")
			# if writing, do this:
			olddir = os.path.join(dir_name, "old")
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


def write_simple(new_content, dir_name, doc_name):
	filepath = os.path.join(dir_name, doc_name)
	sfd = open(filepath, "w")
	sfd.write(new_content)
	sfd.close

	print("New File: " + str(filepath))


def init(aDir):
	"""
	create new journal dir
	:param aDir: a directory to be created if it does not exist.
	"""
	if not os.path.exists(aDir):
		os.makedirs(aDir)


if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1] == "init":
		init(journal_dir)

	print(journal_dir)

# print(dom + dayth_dict[dom])

# todo implement this
def get_prior_dir(search_dir):
	"""search_dir ends with a path like somthing/yyyy/mm
	then the pathname of the prior dir  will be returned"""
	if search_dir == "/":
		return None
	if search_dir[-1] == '/':
		search_dir = search_dir[0:-1]   # get rid of trailing '/' before split
	year_path, month_part = os.path.split(search_dir)
	base_path, year_part = os.path.split(year_path)
	prior_months  = {"01":"12", "02":"01", "03":"02", "04":"03",
					 "05":"04", "06":"05", "07":"06", "08":"07",
					 "09":"08", "10":"09", "11":"10", "12":"11" }
	try:
		year_int = int(year_part)
	except ValueError:
		return None  # bad year

	if month_part not in prior_months.keys():
		return None # bad month

	mm = prior_months[month_part]
	if mm == "12":
		year_int -= 1

	if year_int <= 0:
		return None # underflow year

	year_str = '{:04d}'.format(year_int)
	return os.path.join(base_path, year_str, mm)
