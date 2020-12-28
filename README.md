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
       x - create write_item_to_story_file() to update any item back to it's original story, or add it to a default task list
       d - fix bug where titleHash isn't created for new tasks in default/new task story.md
            - any file read that might have been updated by the user should have the titleHash set if it isn't already present.
                x - add Item method to add_missing_titleHash
                a - legacy code todo: 
                    # todo make saved title hash available as a read only property to
                       be consistent with notes in  Module and Object strategy.md
                x - test Item method for add_missing_titleHash
                x - add Section method add_all_missing_item_titleHash(self)
                a - test Section method a a m th
                x - call a a m t h of document created in load_story_from_file()
                x - call it from the same place that the storySource is set.
                d - fix: tasks from old journal / todo files do not have titleHash when loaded to the new journal / to do.
                    - can deal with by assuring that when they get written, the titleHash gets updated.
                    
                d - update the story in case any new title hashes were added.
            - merging should be simple: the position in the journal comes from the story, but the content comes from todo(aka journal)

    issue: story file item changes will be overwritten if the item is also in journal / to do.   
        - need a way to run tlog with no tasks pushed into in journal / to do so that story groomig can be done.
        - this will eventually happen naturally when the number of daily tasks will subtract off the 
            number of complted tasks, and all tasks are done for the day.

        #The general flow of tlog main should be:

        ## merge has to write all the journal / todo tasks back to source stories or the default story, 
                to persist any modifications.


        ## then read all the stories, 
                adding title hash if missing (per above)
                setting / updating storySource (already happening in load_story_from_file())
            
            find and read the journal (aka todo) file


    


            extract a list of the in progress in todo (aka journal). 
                (build a select only version of---> select_modify_item_tops_by_pattern(pat, TLDocument.unfinished_s) )
                flip them all to unfinished 
            extract a list of the xa (completed or abandoned) in todo (aka journal)
            clean up and simplify the make scrum logic 
                load the resolved_data tasks: the xa list , the 'u -' copies (TL Document scrum.insert_item for all the 'u -' copies, 
                load the todo_data tasks: the 'd -' tasks and '/ -' from the truncated backlog.

        ##Write state
            re-comput title hashes before writing can help subsequent runs detect if an item has been modified.  
                Is this needed? not really, 
                but it should be done if we assume no other consumers re a running against the same set of stories.
                otherwise a more sopisticated merge is needed.
    

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