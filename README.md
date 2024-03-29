README.md
# Task Log background
tlog is a task manager that started as a simple "todo file" manager, and evolved 
with my understanding of how one might roll together goal planning and a "personal scrum"
or "personal kanban" to account for many competing demands that may take you off course
from your planned endeavors.

It is code that I have been using for many years to learn python, and thus has many old 
very badly designed sections of code.

See user documentation at [Tlog User Doc.md](docs/Tlog%20User%20Doc.md)
See [programmer doc.md](docs/programmer%20doc.md) for information about coding and contributing to this project.
See (https://github.com/psons/tldbin README.md) for scripts to assemble a testing and
development environment.

# current work
On a feature or fix branch, paste the current story text 
from the backlog into here.

## current work tasks

## This section is the change summary for non-trivial commit increments.
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

### 2023-02-08
Journal file is now called Blotter.
Now writes latestSprint.txt into temp dir with an Endeavor and Story level summary of the sprint.

# Modeling tasks over time time in the task blotter
(aspirational notes)
 1. Future: The EffortDomain class is the model for Endeavor management
    - has file system representation in fsendeavor.py
 
 2. Present: The Sprint class is the model for the curently selected task execution.
    - the terms todo ir task blotter refer to the apps that work on the Sprint.
 
 3. Past: The Journal is the model for the Resolved tasks, and any notes and references 
 that may be captured alogn the way.
    - rename journaldir.py to be fsjournal.py 
