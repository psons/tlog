README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work

Tasks in this effort are flowing in from:
    ~/journal/Endeavors/tl_sprint/tasks in Mongo story.md

Notes and learning are being recorded in:
    ~/dev/tl2/Planning/Technical Implementation Notes/Mongo and Domain model notes.md

## current work tasks

x - Write a method in Section class to get the body data, which is the body_items, but skipping any 'meta data only'
items, such as typically the first Item.
 - this prevents the sprint from having a blank item at the beginning.

x - build a python domain model to load 1 endeavor and put it in mongo
  x - explore enhancing the Endeavor to extract a raw python structure of dicts, lists, and strings.  
   This should be serializable with simplejson and probably any other serialization library
   x - need to understand simpleJson better.
        - simple json is the externally maintain standard package for json.
   x - write a json encode of a simple flat object.
    x - write a simple method to getEncodable data from the Python class.
        - see which types are encodable: https://docs.python.org/3/library/json.html#encoders-and-decoders
    x - feed the encodable data as a dict to json dumps() https://docs.python.org/3/library/json.html#basic-usage
    x - need to make an Endeavor test suite.
    x - integrate tlog file system implementation with the endevor.Endeavor objects
        x - add a document attribute storyName and set it to so that tlog.endeavor_story_docs 
        is a list of TLDocuments, that can be used to build the endeavor.Endeavors.
        x - class StoryGroup that has tests.  Unwind the following to do it in two steps.
      x - 1. - get the StoryGroups
          1.a. build endeavor.Endeavor as from the StoryGroups.
      x - 2. - get a list of the story docs from all the story groups.
        endeavor_story_docs: List[TLDocument] = [story_doc for sdo in story_dir_objects
                                             for story_doc in StoryGroup(sdo).story_docs ] #  .get_short_stories()]
        x - write StoryGroup.as_endeavor()
x -  provide an _id based on eid for mongo use. 

todo Mongo tasks in mongocol:
  x - set attribute _id as eid in the data structure.
  a - test endeavors.insert_many or update many with upsert=True
  x - change upsert_endeavor to actually upsert, not insert


# Project notes
See docs/programmer doc.md for infomation about coding and contributing to this project.

## This section is the change summary for non trivial commit increments.
### 2022-07-09 commit
Work is beginning to store the domain model im Mongo DB.
Moved constant directory names and file patterns to tlconst.apCfg to clean up and document better.
Move constant names in TLDocument to module scope
Basic insert to Mongo supported
