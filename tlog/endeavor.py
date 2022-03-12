# the model of endeavors, and the stories and tasks tha make them up
# this model is agnostic of:
#  - parsing and storage representation.
#  - semantic meaning of attributes
from __future__ import annotations
from typing import List


class Endeavor:
    """
    An endeavor is a goal like thing to achieve.  It is much like a agile epic, in that it will end up being
    fulfilled through multiple stories that likely, at the outset are not fully understood or enumerated.
    See tlog user documentation.
    This Endeavor type will not have any of the information about how to represent or store Endeavors
    """
    def __init__(self, name):
        self.name
        self.storyList: List[Story] = []  # in priority order

    def getEncodable(self):
        for key in sorted(self.__dict__.keys()):
            print(f"key: {key}")

class Story:
    def __init__(self, name, parentEndeavor, taskList: List[Task]):
        self.maxTasks: int
        self.name = name
        self.parentEndeavor: Endeavor = parentEndeavor
        self.taskList: List[Task] = taskList

class Task:
    def __init__(self, status: str, title: str, detail: str, parentStory: Story ):
        self.status = status
        self.title: str = title
        self.detail: str = detail
        self.parentStory: Story = parentStory

