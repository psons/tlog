# the model of endeavors, and the stories and tasks that make them up
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
    An an_endeavor is a goal like thing to achieve.  It is much like a agile epic, in that it will end up being
    fulfilled through multiple stories that likely, at the outset are not fully understood or enumerated.
    See tlog user documentation.
    """
    name_key: str = 'name'
    max_stories_key: str = 'maxStories'
    eid_key: str = '_id' # name _id is used as key in Mongo.
    story_list_key = 'story_list'
    def __init__(self, name, max_stories=None, eid=None):
        # todo: change max_stories to max_tasks.  It should be a total number of stories the endeavor can
        #   contribute to the sprint.   If a user desires more stories to contribute, it can be done by
        #   reducing the the max_tasks in the top stories.
        self.name = name    # todo: it should not be possible to make an Endeavor with null or empty Name,
                            #   which would result a common unique eid.
        # the UI is working differently: has a max tasks for the
        # endeavor
        self.max_stories = max_stories or tldocument.default_max_stories
        self.eid = eid or digest(self.name)
        self.story_list: List[Story] = []  # in priority order

    def __str__(self):
        return f"{self.__class__.__name__} : {self.name}, {self.eid}"

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.eid}"

    def add_story(self, a_story: Story):
        """This should typically only be called from Story.__init__()"""
        self.story_list.append(a_story)


    def as_encodable(self):
        """"Return self as python structures that the json module or other serializers can encode"""
        return_dict = {}
        return_dict[Endeavor.name_key] = self.name
        return_dict[Endeavor.max_stories_key] = self.max_stories
        return_dict[Endeavor.eid_key] = self.eid
        return_dict[Endeavor.story_list_key] = [story.as_encodable() for story in self.story_list]
        return return_dict

    @staticmethod
    def obj_from_encodable(data: Dict)-> Endeavor:
        f"""
        Will raise keyerror if the expected keys are not found.
        The constructor wil assign values if data does not contain keys 
        {Endeavor.eid_key} and {Endeavor.max_stories_key}
        :param data: A dictionary expected to contain keys
         {Endeavor.name_key} and {Endeavor.story_list_key}
        :return: and Endeavor object constructed from the data passed in 
        """
        if Endeavor.eid_key in data:
            eid_val = data[Endeavor.eid_key]
        else:
            eid_val = None

        if Endeavor.max_stories_key in data:
            max_stories_val = data[Endeavor.max_stories_key]
        else:
            max_stories_val = None

        theEndeavor = Endeavor(
            data[Endeavor.name_key],
            max_stories=max_stories_val,
            eid=eid_val
        )
        for story_dict in data[Endeavor.story_list_key]:
            Story.obj_from_encodable(story_dict, theEndeavor)  # Story uses a callback to add itself to the Endeavor
        return theEndeavor


class Story:
    # keys for encoding and decoding to/from Python Dict and List structures.
    max_tasks_key: str = 'maxTasks'
    name_key: str = 'name'
    sid_key: str = 'sid'
    task_list_key: str = 'taskList'
    def __init__(self, name, parent_endeavor, max_tasks=None, sid=None):
        self.name = name
        self.parent_endeavor: Endeavor = parent_endeavor
        self.max_tasks: int = max_tasks or tldocument.default_maxTasks
        self.sid = sid or f"{self.parent_endeavor.eid}.{digest(self.name)}"
        self.task_list = []
        self.parent_endeavor.add_story(self) # so that parent an_endeavor knows this story is part of it.

    def add_task(self, a_task: Task):
        self.task_list.append(a_task)

    def __str__(self):
        return f"{self.__class__.__name__} : {self.name}, {self.sid}"

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.sid}"

    def as_encodable(self):
        """"Return self as python structures that the json module or other serializers can encode"""
        return_dict = {}
        return_dict[Story.max_tasks_key] = self.max_tasks
        return_dict[Story.name_key] = self.name
        return_dict[Story.sid_key] = self.sid
        return_dict[Story.task_list_key] = [task.as_encodable() for task in self.task_list ]
        return return_dict

    @staticmethod
    def obj_from_encodable(data: Dict, parent_endeavor)-> Story :
        f"""
        Will raise keyerror if the expected keys are not found.
        The constructor wil assign values if data does not contain keys 
        {Story.max_tasks_key} and {Story.sid_key}
        :param data:  A dictionary expected to contain key {Story.name_key}
        :param parent_endeavor: The Endeavor object that the resulting story 
        will be registered with.
        :return: Story object constructed from python data structures that results from json.loads()
        or other de-serializers 
        """

        if Story.max_tasks_key in data:
            max_task_val = data[Story.max_tasks_key]
        else:
            max_task_val = None  # will trigger a default in the constructor
        if Story.sid_key in data:
            sid_val = data[Story.sid_key]
        else:
            sid_val = None  # will trigger a default in the constructor
        theStory = Story(
            data[Story.name_key],
            parent_endeavor,
            max_tasks=max_task_val,
            sid=sid_val
        )
        for task_dict in data[Story.task_list_key]:
            Task.obj_from_encodable(task_dict, theStory)  # Task uses a callback to add itself to the Story

        return theStory


class Task:
    status_key: str = 'status'
    title_key: str = 'title'
    detail_key: str = 'detail'
    tid_key: str = 'tid'

    def __init__(self, status: str, title: str, parent_story: Story, detail: str=None, tid=None):
        """
        Task object holds the user created status, title and detail for a task.  It also has a
        reference to the parent story that it is a part of, and a task ID (tid) that identifies it for its life.

        The valid status values with their meaning are defined in tldocument.Docsec

        :param status:
        :param title:
        :param detail:
        :param parent_story:
        :param tid:
        """
        if status not in tldocument.task_status_names:
            raise tlutil.TaskSourceException(f"{status} is not a recognized task status")
            # possibly just warn?
        if parent_story.__class__.__name__ != 'Story':
            raise TypeError(f"A Task must have Story object as its parent.  Found for task title: {title}")
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
        return_dict[Task.status_key] = self.status
        return_dict[Task.title_key] = self.title
        return_dict[Task.detail_key] = self.detail
        return_dict[Task.tid_key] = self.tid
        return return_dict

    @staticmethod
    def obj_from_encodable(data: Dict, parent_story: Story)-> Task :
        f"""
        Return a Task object constructed from python data structures that results from json.loads()
        or other de-serializers
        Will raise keyerror if the expected keys are not found.
        The constructor wil assign a value if data does not contain key {Task.tid_key}.
        The key {Task.detail_key} can be absent or empty.
        :param data: A dictionary expected to contain keys {Task.status_key} and {Task.title_key}
        :param parent_story: The Story object that the resulting task will be registered with.
        :return: The Task object  
        """

        if Task.detail_key in data:
            detail_val = data[Task.detail_key]
        else:
            detail_val = ""
        if Task.tid_key in data:
            tid_val = data[Task.tid_key]
        else:
            tid_val = None  # will trigger a default in the constructor

        # will accept keyerror raised by python if Task.status_key, Task.title_key are not found.
        theTask = Task(data[Task.status_key], data[Task.title_key], parent_story, detail_val,
                       tid=tid_val)
        return theTask


if __name__ == '__main__':
    # print(Endeavor("Write a tlog Server").__repr__())
    print("Test code is in testEndeavors.py")
