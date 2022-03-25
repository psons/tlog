# this content should be supported in docstrings.

The domain object model is being created in endeavor.py 
to support representing Endeavors, Tasks, and Stories in an 
encoding agnostic way.

The json encoding and decoding of things in endeavor.py 
does not know the semantic meaning of things, and simply uses the
attribute names and structure of python types returned by 
endeavor.Endeavor.get_encodable().

The text file way of storing the model is in docsec.py, which
is evolving to a markdown extension that is a human editable 
document that has sections with items under them, which also 
supports attributes for documents, sections and items.

The tlog semantic encoding to be used with documents, 
sections and items should be in tldocument.py

The semantics in tldocument.py must match the endeavor.py
semantics.  Task statuses for example have a regex that 
is part of the editor UI contract 'x - ' means completed, 
but here is a regex to tolerate variable user entry like
'/ - ' or '\ - ' for in progress, so tldocument.py will 
hold the semantic meaning encoding for things, and
endeavor.py will import it.



