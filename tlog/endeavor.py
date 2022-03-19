# the model of endeavors, and the stories and tasks tha make them up
# this model is agnostic of:
#  - parsing and storage representation.
#  - semantic meaning of attributes
from __future__ import annotations
from typing import List

# todo conform to pep8 python style
class Endeavor:
    """
    An endeavor is a goal like thing to achieve.  It is much like a agile epic, in that it will end up being
    fulfilled through multiple stories that likely, at the outset are not fully understood or enumerated.
    See tlog user documentation.
    """
    def __init__(self, name):
        self.name = name
        self.storyList: List[Story] = []  # in priority order

    def __str__(self):
        return str(f"{self.__class__.__name__} : {self.name}")

    def add_stories(self, stories: List[Story]):
        self.storyList += stories # todo test this...

    def get_encodable(self):
        for key in sorted(self.__dict__.keys()):
            print(f"key: {key}")

    # todo: make a key property, initially as a hash of the name


    # todo: implement the key attribute for story and task too, but concat the parent keys too.
class Story:
    def __init__(self, name, parentEndeavor, taskList: List[Task]):
        self.maxTasks: int
        self.name = name
        self.parent_endeavor: Endeavor = parentEndeavor
        self.taskList: List[Task] = taskList

class Task:
    def __init__(self, status: str, title: str, detail: str, parentStory: Story ):
        """

        :type parentStory: object
        """
        self.status = status
        self.title: str = title
        self.detail: str = detail
        self.parent_story: Story = parentStory

if __name__ == '__main__':
    # print(Endeavor("Write a tlog Server").__repr__())
    endeavor1 = Endeavor("Write a tlog Server")
    story1: Story("Build a domain model", endeavor1, )
    print(endeavor1)
