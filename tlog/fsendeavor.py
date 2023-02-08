# todo Build a FileSystemDomain class that has the user_path_obj.endeavor_file path and a list of
# todo make a FileSystemEndeavor class that keeps info about an Endeavor persisted in a file system.
# todo re-implement journaldir.load_endeavor_stories(user_path_o) as a method of the EndeavorDomain class
# todo build a EffortDomain class Endeavor Creator
# From Task Blotter
# type EndeavorT = {
#     _id: string;
#     name: string;
#     maxStories: number
#     eid:  string;
#     story_list: StoryT[]
# }
#
# interface UserDomainT {
#     name: string;               // a name of a "EffortDomain" of effort and Endeavors.
#                                 // See user documentation.
#
#     sprint_max_tasks: number;  // the ultimate constraint of tasks in a sprint.
# }
#
# export const user_domain: UserDomainT = {
#     name: "Daydreaming time",
#     sprint_max_tasks: 6
# }
import os
import re
from typing import List

import journaldir
import tldocument
from endeavor import Endeavor, Story, Task, EffortDomain
from journaldir import UserPaths, read_file_str, StoryDir
from tlconst import apCfg


# Keeps data about a file system based task domain
from tldocument import BlotterDocument


class FileSystemDomain:

    def __init__(self, path_object: UserPaths):
        self.endeavor_path = path_object.endeavor_path
        self.endeavor_file = path_object.endeavor_file
        self.file_system_endeavors: [FileSystemEndeavor] = []
        self.load_fs_endeavors()

    def load_fs_endeavors(self):
        endeavor_text: str = apCfg.default_endeavor_name + " 2" + "\n" + read_file_str(self.endeavor_file)
        endeavor_text = endeavor_text.rstrip()
        for data_line in endeavor_text.split('\n'):
            matched = re.match(r'(\w+)\W+(\d+)', data_line) # w is word characters.  W is not word characters
            endeavor_name = matched.group(1)
            max_stories = matched.group(2)
            self.file_system_endeavors.append(
                        FileSystemEndeavor(max_stories, StoryDir(os.path.join(self.endeavor_path, endeavor_name)))
            )

    def get_all_story_dirs(self):
        return [fse.story_dir for fse in self.file_system_endeavors]

    def as_domain(self):
        domain: EffortDomain = EffortDomain("Paul hard-coded domain name", 6)
        for fse in self.file_system_endeavors:
            domain.endeavors.append(fse.as_endeavor())
        return domain

class FileSystemEndeavor:
    """
    Adds story semantics around a group of Documents read from files in a directory
    Combines the journaldir.StoryDir and the tldocument.BlotterDocument to get
    a collection of tasks.
    Sets attributes in the tasks in the Documents to allow changes in the tasks to be written back to the
        storySource: an_endeavor/story
    journal to be written back to the original stories
    """

    story_source_attr_name = "storySource"

    def __init__(self, max_stories: int, story_dir: StoryDir):
        self.max_stories = max_stories
        self.story_dir = story_dir
        self.story_docs: List[BlotterDocument] = [load_and_resave_story_file_with_attribs(s_file)
                                                  for s_file in self.story_dir.story_list]

    def get_endeavor_name(self):
        return os.path.basename(self.story_dir.path)

    def as_endeavor(self) -> Endeavor:
        endeavor = Endeavor(self.get_endeavor_name())
        endeavor.max_stories = self.max_stories
        for story_doc in self.story_docs:
            story = Story(story_doc.story_name, endeavor, story_doc.max_tasks)
            for task_item in story_doc.get_document_matching_list(tldocument.unresolved_pat):
                # todo first arg below needs to be the status.  prob implement a taskItem.get_status()
                # todo is this right for last arg?: str(taskItem.subs)
                Task(tldocument.find_status_name(task_item.get_leader()), task_item.get_title(), story,
                     task_item.detail_str())
        return endeavor

    def __str__(self):
        return "\n".join([str(d) for d in self.story_docs])




def load_and_resave_story_file_with_attribs(file_name) -> BlotterDocument:
    """
    Loads a file system file as a BlotterDocument and saves it back to disk with the following enrichment:.
        Adds 'storyName:' to the BlotterDocument representing a Story.
            This enable the story to be migrated to an object store.
        adds 'storySource:' 'titleHash:' to each task item in the BlotterDocument
            These attributes enable items to be re titled and still update the original story file.
    """
    story_doc: BlotterDocument = load_doc_from_file(file_name)
    story_doc.attribute_all_unresolved_items(FileSystemEndeavor.story_source_attr_name, file_name)
    story_doc.for_journal_sections_add_all_missing_item_title_hash()
    story_name = os.path.basename(file_name)
    story_name = re.sub(apCfg.story_suffix_pat, '', story_name)
    story_doc.story_name = story_name
    journaldir.write_filepath(str(story_doc), file_name)
    return story_doc


def load_doc_from_file(file_name) -> BlotterDocument:
    file_text = journaldir.read_file_str(file_name)
    tl_doc = BlotterDocument.fromtext(file_text)
    return tl_doc
