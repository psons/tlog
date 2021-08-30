# the model of endeavors, and the stories and tasks tha make them up
# this model is agnostic of:
#  - parsing and storage representation.
#  - semantic meaning of attributes
from __future__ import annotations
from typing import List


class Endeavor:
    """
    An endeavor is a goal like thing to achieve.  It is much like a agile epic, in that it will end up being
    fulfilled through multiple stories that likely, at the outset are not full understoold or enumerated.
    See tlog user documentation.
    This Endeavor type will not have any f the information about how to represent or store Endeavors
    """
    def __init__(self, name):
        self.name
        self.storyList = []  # in priority order

class Story:
    def __init__(self, name, parent, taskList: List[Task]):
        self.name = name
        self.parent: Endeavor = parent
        self.taskList: List[Task] = taskList

class Task:
    def __init__(self, status: str, title: str, detail, str ):
        self.status = status
        self.title: str = title
        self.detail: str = detail

