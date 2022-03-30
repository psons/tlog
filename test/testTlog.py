import unittest
from tldocument import TLDocument
import journaldir
from tlog import StoryGroup


from test_journaldir import test_storydir_str
from testdata import getUnitTestUserPathObject
# from Endeavors/aGoal/small story.md
upo = getUnitTestUserPathObject()
expected_story_text= f"""\
storyName:small story
maxTasks: 3
d - start on the small story
storySource:{upo.endeavor_path}/aGoal/small story.md
titleHash:5e874c75f0
d - some more work on the small story
storySource:{upo.endeavor_path}/aGoal/small story.md
titleHash:4db4f19abf
d - refine the small story work
storySource:{upo.endeavor_path}/aGoal/small story.md
titleHash:961443447d
d - finish the small story!
storySource:{upo.endeavor_path}/aGoal/small story.md
titleHash:6ae341e0a3"""
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

