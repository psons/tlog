import unittest
import json
from endeavor import Endeavor, Story, Task

endeavor1 = Endeavor("Write a tlog Server")
story1: Story = Story("Build a domain model", endeavor1)

task1: Task = Task('d', "Make basic Endeavor, Story, and Task objects", story1, "figure out how objects nest")
j_indent = 2

expected_json_of_endeavor1 = """{
  "name": "Write a tlog Server",
  "maxStories": 3,
  "eid": "8a60ec61a9",
  "story_list": [
    {
      "maxTasks": 1,
      "name": "Build a domain model",
      "sid": "8a60ec61a9.bfce9ff884",
      "taskList": [
        {
          "status": "d",
          "title": "Make basic Endeavor, Story, and Task objects",
          "detail": "figure out how objects nest",
          "tid": "8a60ec61a9.bfce9ff884.04b5400ca6"
        }
      ]
    }
  ]
}"""


expected_json_of_story1 = """{
  "maxTasks": 1,
  "name": "Build a domain model",
  "sid": "8a60ec61a9.bfce9ff884",
  "taskList": [
    {
      "status": "d",
      "title": "Make basic Endeavor, Story, and Task objects",
      "detail": "figure out how objects nest",
      "tid": "8a60ec61a9.bfce9ff884.04b5400ca6"
    }
  ]
}"""

expected_json_of_task1 = """{
  "status": "d",
  "title": "Make basic Endeavor, Story, and Task objects",
  "detail": "figure out how objects nest",
  "tid": "8a60ec61a9.bfce9ff884.04b5400ca6"
}"""

class TestEndeavor(unittest.TestCase):
    """Unit tests for the Endeavor class"""
    def __init__(self, *args, **kwargs):
        super(TestEndeavor, self).__init__(*args, **kwargs)
        self.json_of_endeavor1 = json.dumps(endeavor1.as_encodable(), indent=j_indent)

    def testEndeavorWhole(self):
        self.assertEqual(expected_json_of_endeavor1, self.json_of_endeavor1)

    def testJsonSymmetry(self):
        """
        loads json back into an Endeavor, and then turns that Endeavor back into json,
        and tests that the json is the same as the original
        """
        endeavor_from_json = Endeavor.obj_from_encodable(json.loads(self.json_of_endeavor1))
        json_of_endeavor1_after_loads = json.dumps(endeavor_from_json.as_encodable(), indent=j_indent)
        # print(f"Original Endeavor1 json:\n{self.json_of_endeavor1}")
        # print(f"Endeavor1 json after loads:\n{json_of_endeavor1_after_loads}")
        self.assertEqual(expected_json_of_endeavor1, json_of_endeavor1_after_loads)


class TestStory(unittest.TestCase):
    """Unit tests for the Story class"""

    def __init__(self, *args, **kwargs):
        super(TestStory, self).__init__(*args, **kwargs)
        self.json_of_story1 = json.dumps(story1.as_encodable(), indent=j_indent)

    def testStoryWhole(self):
        # print(self.json_of_story1)
        self.assertEqual(expected_json_of_story1, self.json_of_story1)


task_json_no_detail_tid_key = """{
  "status": "d",
  "title": "Make basic Endeavor, Story, and Task objects"
}"""

task_json_no_status_key = """{
  "title": "Make basic Endeavor, Story, and Task objects",
  "detail": "",
  "tid": "8a60ec61a9.bfce9ff884.04b5400ca6"
}"""

task_json_no_title_key = """{
  "status": "d",
  "detail": "",
  "tid": "8a60ec61a9.bfce9ff884.04b5400ca6"
}"""



tjndtk_dumps = """{
  "status": "d",
  "title": "Make basic Endeavor, Story, and Task objects",
  "detail": "",
  "tid": "8a60ec61a9.bfce9ff884.04b5400ca6"
}"""

class TestTask(unittest.TestCase):
    """Unit tests for the Task class"""
    def __init__(self, *args, **kwargs):
        super(TestTask, self).__init__(*args, **kwargs)
        self.json_of_task1 = json.dumps(task1.as_encodable(), indent=j_indent)

    def testTaskWhole(self):
        # print(self.json_of_task1)
        self.assertEqual(expected_json_of_task1, self.json_of_task1)

    def testTaskJsonNoDetailKey(self):
        """
        test task with no detail provided is empty string
        test task with no tid provided is calculated
        """
        tjndk = Task.obj_from_encodable(json.loads(task_json_no_detail_tid_key), story1)
        tjndk_json = json.dumps(tjndk.as_encodable(), indent=j_indent)
        # print(tjndk_json)
        self.assertEqual(tjndtk_dumps, tjndk_json)


    def testTaskJsonNoStatusKey(self):
        f"""
        test that KeyError is raised if there is no key: {Task.status_key}
        """
        with self.assertRaises(KeyError):
            Task.obj_from_encodable(json.loads(task_json_no_status_key), story1)


    def testTaskJsonNoTitleKey(self):
        f"""
        test that KeyError is raised if there is no key: {Task.title_key}
        """
        with self.assertRaises(KeyError):
            Task.obj_from_encodable(json.loads(task_json_no_title_key), story1)


