README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work
Important to build on Tlog focus Strategy.txt by getting prioritized.md

Prioritized Backlog story.md
A Prioritized.md file is used to sequence the names of files in an endeavor dir.

# tasks

d - provide logging for each update / insert case when adding an item to a document and section.
d - section support to do head or tail insert of new items.

All tasks from files without an entry in Prioritized.md come after prioritized ones.
x - check dirs to be scanned for [pP]roioritized.[mM][Dd]
x - build file_list from prioritized
x - append any files with tasks that are not in prioritized.md


d - eliminate the TLDocument special section "in_progress" it isn't needed any more.  Some tests will break.
            - left over from todo: 2020-12-20 write_xa (from tlog.py) from TL focus.md or Writeback 2 story.md ot Tlog focus Strategy.txt

d - test reading a story

d - test write back 'x-'  
 - given a 'x -' task in the journal section (or later sprint section) of the current doc file story with a storySource Attribute: 
 - when tlog is run
 - then 
    the task story is written to the StorySource File
    and reading the story from the story source file matches the task as it is in the journal section

d - test write back 'a-'  
 - given a 'a -' task in the journal section (or later sprint section) of the current doc file story with a storySource Attribute: 
 - when tlog is run
 - then 
    the task story is written to the StorySource File
    and reading the story from the story source file matches the task as it is in the journal section

d - implement '/ -' (in progress) write back
 - do work to try and pass: test write back '/-'

d - test write back '/-'  
 - given a '/ -' task in the journal section (or later sprint section) of the curent doc file story with a storySource Attribute: 
 - when tlog is run
 - then 
    the task story is written to the StorySource File
    and reading the story from the story source file matches the task as it is in the journal section
   
d - test removing xa tasks from source stories.

# Project notes
Add more explanatory notes about the project.

[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)