README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work

Tasks in this effort are flowing in from:
    Mongo and File Integration sameness story.md

Notes and learning are being recorded in:
    tldev/../Planning/*

## current work tasks
x - allow the leader 's - ' in an endeavor story to be handled as a task that gets selected to the task blotter.
x - read 's - ' from the blotter
 - paralell the behavior of 'resolved' in that they are pulled into a special section, '# Scheduled for later'
    x - write '# Scheduled for later' at the end of the blotter.
x - in step tlog main step 11, the scrum object is written to file as a list of tasks
 - enhance this to include a scheduled section. 
x - Problem: Tasks taged as 's' are not being written back to the Endeavor/story.
       - get_document_unresolved_list uses unresolved_pat to get '/' and 'd' to write them back to
       - an Endeavor/story.  If I add 's' to unresolved_pat, it will also be potentially pulled into a 
         daily todo list.
       - This gives rise to the idea that 
         - when building a task blotter, tasks should be 
           separated into # sections by type as when they are added to a doc
         - when reading a file, typically the section grouping of tasks should be preserved, 
           or possibly ignored.
   x - deprecate get_document_unresolved_list().  
   x - replace it with get_document_items_by_pattern(pattern)
         - replace the write-back usage of get_document_unresolved_list() with get_document_items_by_pattern(write_back_pat)
         - replace the attribute all usage of get_document_unresolved_list() with get_document_items_by_pattern(write_back_pat)
         - replace scrum candidate usage of get_document_unresolved_list() with get_document_items_by_pattern(today_work) 

# Project notes
See docs/programmer doc.md for information about coding and contributing to this project.

## This section is the change summary for non trivial commit increments.
### 2022-07-09 commit
Work is beginning to store the domain model in Mongo DB.
Moved constant directory names and file patterns to tlconst.apCfg to clean up and document better.
Move constant names in TLDocument to module scope
Basic insert to Mongo supported

### 2022-08-22
Adding scheduled as a task status.
Removing 'u - ' as a status that gets written into the resolved file: it has limited benefit, 
    and pollutes search results if a task goes unfinished for multiple days.