README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work

Tasks in this effort are flowing in from:
    ~/journal/Endeavors/tl_sprint/tasks in Mongo story.md

Notes and learning are being recordeed in:
    ~/dev/tl2/Planning/Technical Implementation Notes/Mongo and Domain model notes.md

# tasks

d - build a python domain model to load 1 endeavor and put it in mongo
 - explore enhancing the Endeavor to extract a raw python structure of dicts, lists, and strings.  
   This should be serializable with simplejson and probably any other serialization library
   x - need to understand simpleJson better.
   d - write a json encode of a simple flat object.
    d - write a simple method to getEncodable data from the Python class.
        - see which types are encodable: https://docs.python.org/3/library/json.html#encoders-and-decoders
    d - feed the encodable data as a dict to json dumps() https://docs.python.org/3/library/json.html#basic-usage 
        need to make an Endeavor test suite.   Should base off of test/test_journaldir.py TestStoryDir(TestCase)
   in which a StoryDir is really an Endeavor saved in a directory structure.
    - StoryDir has the path to the StoryDir, and should be enhanced with 
        - the 'name' of tha last dir on the path, (aka the Endeavor name) 
        - and a hash of that 'name' (aka the EID)
    - call a simple constructor for the Endeavor with the above two attributes.

    - prob get the Story domain obj from info in the StoryDoc.
        - add the 'name' as the file name prob minus the ' story.md' ending
        - figure out how to get the list of tasks.

   Before step #8, tlog has the list of story Docs as TLDocument objects, but they are a flat list, not underneath Endeavors.
    - they do have story source paths so they can be written back.


# Project notes
Work is beginning to store the domain model im Mongo DB.
Moved constant directory names and file patterns to tlconst.apCfg to clean up and document better.

[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)