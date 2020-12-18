import unittest
from tldocument import TLDocument
import journaldir
from tlog.tlog import StoryGroup


from test_journaldir import test_storydir_str

# from Endeavors/aGoal/small story.md
expected_story_text= """\
maxTasks: 3
d - start on the small story
storySource:/Users/paulsons/dev/tl2/testuser/testjournal/Endeavors/aGoal/small story.md
d - some more work on the small story
storySource:/Users/paulsons/dev/tl2/testuser/testjournal/Endeavors/aGoal/small story.md
d - refine the small story work
storySource:/Users/paulsons/dev/tl2/testuser/testjournal/Endeavors/aGoal/small story.md
d - finish the small story!
storySource:/Users/paulsons/dev/tl2/testuser/testjournal/Endeavors/aGoal/small story.md\
"""
sd = journaldir.StoryDir(test_storydir_str)

class TestTlog(unittest.TestCase):

	# todo should this test something about the state of the object?
	def testStoryGroupConstructor(self):
		"""doesn't test anything but runs constructor"""
		story_group = StoryGroup(sd)
		# print(story_group)
		self.assertEqual("pass", "pass")

	def testKnownStoryInGroup(self):
		story_group = StoryGroup(sd)
		first_story = story_group.story_docs[0]
		# print("first_story", first_story)
		self.assertEqual(expected_story_text, str(first_story))

