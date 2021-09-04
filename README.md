README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work

Created unit_test_tmp_dir.py to establish a unit test temp dir (uttd) as a root path for file system 
operations needed by unit tests.

It is used for by testdata.getUnitTestUserPathObject() to get a path object that will not interfere with other 
test and user environments.

tlog now keeps only a single journal file in the jounaldir/yyyy/mm directory
tlog now moves resolved files into a subdirectoy of jounaldir/yyyy/mm

# tasks
x - single journal file in the month directory
 - when writing a jtd story, move any old jtd to an 'old' subdir of the temp location. 
 x - write method in journaldir.py to get listing of files matching a pattern given as an arg
    - already have: 
        get_file_names_by_pattern(dir_name, a_pattern) -> List[str]:
 x - initialize ~/tmp/tlog/old if it doesn't exist.     
 x - write method in journaldir.py to move list of files to target dir
      x - write tests.
 x - write method in tlog.py to 
   x - call journal dir method to get listing per above.
   a - remove current jtd file from list.  
      - leave it there.  it will be immediately rewritten.  
        a diff with the old copy can show what just changed. 
   x - call journal dir method to move files. 



# Project notes
Add more explanatory notes about the project.

[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)