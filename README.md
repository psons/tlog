README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work

Tasks in this effort are flowing in from:
    Mongo and File Integration sameness story.md

Notes and learning are being recorded in:
    tldev/../Planning/Technical Implementation Notes/Mongo and Domain model notes.md

## current work tasks
storyName:Mongo and File Integration sameness story

Story goal is to code and test round trip read Endeavors, save to mongo, read back
and write to files without loss of information.  The stories written back may be enhanced 
with some key info needed to locate tasks in te endeavors mongo collection, just as 
tasks are stored in a storydir in the file system.

put another way:
    File system state (committed Git) 
        -> Story Dir markdown 
        -> Object -> encodable -> write Mongo 
        -> read Mongo -> JSON? -> Object -> StoryDir 
        -> File system state: Git diff should be same. 

d - object from Mongo
storySource:/Users/paulsons/journal/Endeavors/tl_july/Mongo and File Integration sameness story.md
titleHash:d39a6200c5
 - read Mongo -> JSON? -> Endeavor Object

d - make an integration test directory and a testMongo class.
storySource:/Users/paulsons/journal/Endeavors/tl_july/Mongo and File Integration sameness story.md
titleHash:aeaac60d35

d - Object to mongo and back
storySource:/Users/paulsons/journal/Endeavors/tl_july/Mongo and File Integration sameness story.md
titleHash:04502d00b3
 - integration test to verify Endeavor Object -> encodable -> write Mongo -> read Mongo -> JSON? -> Endeavor Object

d - create Story Dir markdown from Endeavor Object
storySource:/Users/paulsons/journal/Endeavors/tl_july/Mongo and File Integration sameness story.md
titleHash:d05255d958
 - add tests too.

d - write Story Dir to file system 
storySource:/Users/paulsons/journal/Endeavors/tl_july/Mongo and File Integration sameness story.md
titleHash:dd15886bcc


# Project notes
See docs/programmer doc.md for infomation about coding and contributing to this project.

## This section is the change summary for non trivial commit increments.
### 2022-07-09 commit
Work is beginning to store the domain model im Mongo DB.
Moved constant directory names and file patterns to tlconst.apCfg to clean up and document better.
Move constant names in TLDocument to module scope
Basic insert to Mongo supported
