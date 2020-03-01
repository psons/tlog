README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# curent work
support endevors file MVP

Pulling tasks from story files will require that tasks already in the journal 
are recognizable if they are the same as the "fresh" version pulled in from the story

	first cut, just pop 1 task out of a 1 story

	If  self.top matches in two Items, ignore the incoming story for now,
	assuming the one in the journal may have updates.
		to compare, write isSameItem(...), and check the list of items in the backlog section to see if the in coming story ids there.  if not, add it. 

will need story to support preferences:
 - maxDaiy tasks #number of tasks to have in a day



Somthing like the user docs in old tlog dir/doc directory.

from user docs:

...
n Endeavor is a thing like a project represented by a directory of stories or a Jira project, or maybe an e-mail account.  It is a set of prioritized "stories" needed to fulfill (or manage) the endeavor.
...
Without any command line arguments, tlog will look for task sources listed in JOURNAL_PATH/endeavors or ~/journal under the users home location native to the operating system distribution and write a task list to a journal directory.

support endeavor dirs story.txt

directories named in endeavors file will be scanned for stories.
# feature branch: endeavors
x - get a list of endeavor dirs
x - sj_file_list_by_dir for each of the list of endeavor dirs.
x - add all the tasks from those stories, just as if they were found in the journal.
d - build a comparator to detect if a story is already in the backlog before adding.
 - keep it simple for now, just compare the self.top ignoring 
	- the leader and trailing whitespace
x - Item get title and tile hash
d - don't add tasks that are already in the journal
 - process the journal first.
 - for now ignore incoming, favoring support for edits in the journal.
	- later support change detection via a hash attribute 
		- or define a way to merge stories.
		Stories need to be built into Document objects,
		    then merge the story backlog into the journal backlog
d - remake the testuser1.ta with the stories renames .txt to .md.
		
		
# Project notes
Add more explanatory notes about the project.

[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)