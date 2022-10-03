README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work

Tasks in this effort are flowing in from:
    Mongo and File Integration sameness story.md

Notes and learning are being recorded in:
    tldev/../Planning/*

## current work tasks

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

### 2022-10-03
Fixed bugs:
  - max tasks was being ignored if there was another document attribute
  - / for in_progress tasks not correctly escaped in pattern.
  - an existing empty section was not always being used for document attributes. 