# High Level Code Organization
## this content should be supported in docstrings.

The domain object model is being created in endeavor.py 
to support representing Endeavors, Tasks, and Stories in an 
encoding agnostic way to facilitate storing in Mongo, or other object stores.

The json encoding and decoding of things in endeavor.py 
does not know the semantic meaning of things, and simply uses the
attribute names and structure of python types returned by 
endeavor.Endeavor.get_encodable().

The text file way of storing the model is in tldocument and docsec.py, which
is evolving to a markdown extension that is a human editable 
document that has sections with items under them, which also 
supports attributes for documents, sections and items.
The tlog semantic encoding to be used with documents, 
sections and items should be in tldocument.py

The semantics in tldocument.py must match the endeavor.py
semantics.  Task statuses for example have a regex that 
is part of the editor UI contract 'x - ' means completed, 
but here is a regex to tolerate variable user entry like
'/ - ' or '\ - ' as meaning the same thing; 'in progress', so tldocument.py will 
hold the semantic meaning encoding for things, and
endeavor.py will import it.

## Analysis of tlog modules
docsec.py contains the objects created to implement tldocument.py to implement the scrum object that separates 
resolved work from task lists.

tldocument.py is contains the class used for any file that may contain tasks:
    - curent and old task blotters (i. e. olds j/td files.)
    - resolved tasks from the current day
    - story files in Endeavor directories

# python environment management
The tlog project dir contains a venv, used in development and testing.
activate that venev, and use pip to install:

## Gitpython
    pip install GitPython
https://gitpython.readthedocs.io/en/stable/
## pymongo
    pip install pymongo
https://pypi.org/project/pymongo/

# Project Organization
[Using this project structure as a guideline](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

[Using this branch strategy](https://nvie.com/posts/a-successful-git-branching-model/)


