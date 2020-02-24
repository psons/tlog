README.md

On a dev branch, paste the current story text 
from the backlog into here.

The previous day header still has the day of month from the 
previous file when showing completed or unfinished tasks.
Should update to not collide with a day that may occur in this month. 
actuall, all headers from the previous file would be there
with day headers from previous months.
Need to just chop them off if a new month has been initialized! 
 - detect if file came from a previous month
 - if from a previous month, 
 
        - chop of the journal
        
            - just dropping journal no good because we loose the attribute Section
            - becomes a problem on tlog.py line 102: journal_document.doc_name
            - keep the first Section if it is an attribute section
            
        - leaving only the in progress and backlog
            - make sure there is an in progress with a section header
                - because the __str__ relies on that header for "today"


Add more explanatory notes about the project.

[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)