README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work
It is really important to get a version of tlog that only shows me 3 tasks.

-->  
1 - make sure write back is working, an writes all story source tasks back to where they came from.
	1a - make tests for write back.
---


d - do stories relating to flow to fix strange behaviors 
left from write back to story story.md
The following is pulled from user doc, and should be reconciled with 
story texts.
 
### The User Flow.
#### Day 1
1. Create Endeavor directories with story.md files containing tasks.

2. Run tlog, and a daily task file will be created in the journal directory.
 (obsolete: journal-2019-11-16.md is the task file)
 tasks-2019-11-16.md.  Since no journal file exists, and no task file exists 
 matching the date, they will be created. 

3. Mark a few tasks as complete or abandoned, and run tlog again.  
The completed and abandoned tasks will be updated in the source 
story, and moved out of the task file and into the to the 
journal-yyyy-mm-dd.md file for the day (in the journal directory).
_Should new tasks be pulled into the tasks file?  No for now 2020-04-19_
#### Day 2
1. Run tlog, and since no journal file exists, and no task file exists 
 matching the date, they will be created. New tasks will be pulled 
 according to 
    1. the story level max tasks settings
		
# Project notes
Add more explanatory notes about the project.

[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)