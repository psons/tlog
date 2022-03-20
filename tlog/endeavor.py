# the model of endeavors, and the stories and tasks tha make them up
# this model is agnostic of:
#  - parsing and storage representation.
#  - semantic meaning of attributes
from __future__ import annotations
from typing import List
from typing import Dict

import tlutil
from tlutil import digest
import tldocument


class Endeavor:
    """
    An endeavor is a goal like thing to achieve.  It is much like a agile epic, in that it will end up being
    fulfilled through multiple stories that likely, at the outset are not fully understood or enumerated.
    See tlog user documentation.
    """
    def __init__(self, name, max_stories=None, eid=None):
        self.name = name
        self.max_stories = max_stories or tldocument.TLDocument.default_max_stories
        self.eid = eid or digest(self.name)
        self.story_list: List[Story] = []  # in priority order

    def __str__(self):
        return f"{self.__class__.__name__} : {self.name}, {self.eid}"

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.eid}"

    def add_story(self, a_story: Story):
        self.story_list.append(a_story)


    def as_encodable(self):
        """"Return self as python structures that the json module or other serializers can encode"""
        return_dict = {}
        return_dict['name'] = self.name
        return_dict['maxStories'] = self.max_stories
        return_dict['eid'] = self.eid
        return_dict['story_list'] = [story.as_encodable() for story in self.story_list]
        return return_dict

    @staticmethod
    def obj_from_encodable(data: Dict):
        # todo harden this to deal with or raise exception for missing keys in the dict
        # todo introduce class cxonstants for the string keys.
        theEndeavor = Endeavor(
            data['name'],
            max_stories=data['maxStories'],
            eid=data['eid']
        )
        for story_dict in data['story_list']:
            Story.obj_from_encodable(story_dict, theEndeavor)  # Story uses a callback to add itself to the Endeavor
        return theEndeavor


class Story:
    def __init__(self, name, parent_endeavor, max_tasks=None, sid=None):
        self.name = name
        self.parent_endeavor: Endeavor = parent_endeavor
        self.max_tasks: int = max_tasks or tldocument.TLDocument.default_maxTasks
        self.sid = sid or f"{self.parent_endeavor.eid}.{digest(self.name)}"
        self.task_list = []
        self.parent_endeavor.add_story(self) # so that parent endeavor knows this story is part of it.

    def add_task(self, a_task: Task):
        self.task_list.append(a_task)

    def __str__(self):
        return f"{self.__class__.__name__} : {self.name}, {self.sid}"

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.sid}"

    def as_encodable(self):
        """"Return self as python structures that the json module or other serializers can encode"""
        return_dict = {}
        return_dict['maxTasks'] = self.max_tasks
        return_dict['name'] = self.name
        return_dict['sid'] = self.sid
        return_dict['taskList'] = [task.as_encodable() for task in self.task_list ]
        return return_dict

    @staticmethod
    def obj_from_encodable(data: Dict, parent_endeavor):
        """"
        Return a Story object constructed from python structures that results from json.loads()
        or other de-serializers
        """
        # todo harden this to deal with or raise exception for missing keys in the dict
        # todo introduce class cxonstants for the string keys.
        if 'maxTasks' in data:
            mt_val = data['maxTasks']
        else:
            mt_val = None
        theStory = Story(
            data['name'],
            parent_endeavor,
            max_tasks=mt_val,
            sid=data['sid']
        )
        for task_dict in data['taskList']:
            Task.obj_from_encodable(task_dict, theStory)  # Task uses a callback to add itself to the Story

        return theStory


class Task:
    def __init__(self, status: str, title: str, detail: str, parent_story: Story, tid=None):
        """
        Task object can have the statuses initially defined in docstrings for
        tldocument.Docsec, intended to hold the semantic meaning of the
        strings that can be parsed fom the file system representation.
        patterns for parsing:
        :type parent_story: object
        """
        if status not in tldocument.TLDocument.task_status_list:
            raise tlutil.TaskSourceException(f"{status} is not a recognizes task status")
            # possibly just warn?
        if title == "" or title is None:
            raise tlutil.TaskSourceException(
                f"Task without title is not allowed. Found in Story: {parent_story.name}")
                # possibly just warn?
        self.status = status
        self.title: str = title
        self.parent_story: Story = parent_story
        self.tid = tid or f"{self.parent_story.sid}.{tlutil.digest(self.title)}"
        self.detail: str = detail
        self.parent_story.add_task(self)  # so that parent story knows this task is part of it.

    def __str__(self):
        return f"{self.__class__.__name__} : {self.status} - {self.title}, {self.tid}"

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.tid}"

    def as_encodable(self):
        """"Return self as python structures that the json module or other serializers can encode"""
        return_dict = {}
        return_dict['status'] = self.status
        return_dict['title'] = self.title
        return_dict['detail'] = self.detail
        return_dict['tid'] = self.tid
        return return_dict

    @staticmethod
    def obj_from_encodable(data: Dict, parent_story): # todo add return type here and Story and Endeavor
        """"
        Return a Task object constructed from python structures that results from json.loads()
        or other de-serializers
        """
        # todo harden this to deal with or raise exception for missing keys in the dict
        # todo introduce class constants for the string keys.
        theTask = Task(
            data['status'],
            data['title'],
            data['detail'],
            parent_story,
            tid=data['tid']
        )
        #todo need to add the tasks.

        return theTask



if __name__ == '__main__':
    # print(Endeavor("Write a tlog Server").__repr__())
    print("Test code is in testEndeavors.py")
