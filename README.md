README.md

On a feature or fix branch, paste the current story text 
from the backlog into here.
# current work
write back to story story.md
maxTasks: 2
write back to story story.md
x - track source story story.txt
 - write the story file as task attrib: storySource: endeavor>story
### lift completed tasks in journal back to source story.
x - support abandoned tasks 'a - ' similar to complete.
x - make a 'done' section in the Document.
 - implemented in the class DocumentStructure
 - nested in the Document Class
 - re-engineer Document to have a special_sections map with: 
    a header pattern as a key
    a regex pattern set of leader types to put in the section.
    
    First implement '# Done' as DocumentStructure '# Past Tasks', ['^[aA] *-', '^[xX] *-']
    Then re-implement the backlog as DocumentStructure'# Current Tasks', ['^[dD] *-'])
    
    make a Scrum instance of DocStructure ...
    
x - write daily journal as DocStructure w past and current section instead of the journal.    
x - make current section heading include today's date
x - Document method get_xa_story_tasks()
x - for xa_story_tasks update source stories 
x - limit tasks pulled from a story to the maxTasks: value
x - fix bug: in progress isn't in scrum currently.
x - fix bug: write back obliterating all the other tasks in source story
d - bug: pulling less than max_tasks from for example small story.md  
d - don't count xa against maxTasks read from a story
d - limit the stories in an endeavor to those listed in the prioritized.md
		
# Project notes
Add more explanatory notes about the project.

[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)