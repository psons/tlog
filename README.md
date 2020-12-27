README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work
It is really important to get a version of tlog that only shows me 3 tasks.

Writeback 2 story.md

# tasks
x - test journaldir read_file_str and write_filepath

/ - todo: 2020-12-20 write_xa (from tlog.py)
       change from existing logic that only writes back if 'x -' or 'a -' to...
       logic that always writes back to 'resolved-yyyy-mm-dd.md'...
       and removes the items from the original story file.   Eventually story files become empty.
       the reason to remove them is to keep consistency with the way to manage
       '$JOURNAL_DIR/Endeavors/FollowUpQueue/FollowUp story.md' which must have tasks cleaned out,
       or it would grow forever.
       x - (use the scrum DocStructure to sort this to a section, but then the section has to be built into something stringable to write.)
               See docs/Tlog User Documentation.md for file and section heading info:
                   - the completed and abandoned tasks along with a 'u -' task for any in progress tasks will be moved off to the 'completed-journal-yyyy-mm-dd.md' section heading with a heading of the form  # Resolved yyyy-mm-dd' file for the day.
       x - create write_story_file() to update any item back to it's original sory, or add it to a default task list
       d - fix bug where titleHash isn't created for new tasks in default/new task story.md
       d - make an updated version of write_back_updated_story called rm_item_by_hash(xa_item: Item) that will remove
           any leader with the same title hash as the passed in item.   Useful for removing x and a Items from Endeavor stories.
       d - write the



/ - test write back 'd-' (test unit functionality, separate test will deal with selection) 
 - given a 'd -' task in the journal section (or later sprint section) of the current doc file story with a storySource Attribute: 
 - when tlog is run
 - then 
    the task story is written to the StorySource File
    and reading the story from the story source file matches the task as it is in the journal section

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