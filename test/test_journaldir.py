#!/usr/local/bin/python3
import os
import unittest

import tlutil
from tlconst import apCfg
# tlog stuff
from pathlib import Path
from typing import List
from unittest import TestCase
import unit_test_tmp_dir
import tl_testdata
import journaldir

if __name__ == '__main__':
    unittest.main()

prior_dir_cases = [
    ("/U/journal/2020/02/journal-2020-02-17.txt", None),
    ("/U/journal/2020/02/", "/U/journal/2020/01"),
    ("/U/journal/2020/02", "/U/journal/2020/01"),
    ("/U/journal/2020/0", None),
    ("/U/journal/2020", None),
    ("/U/journal/20/02", "/U/journal/0020/01"),
    ("/U/journal/0/02", None),
    ("/U/journal/2020/01", "/U/journal/2019/12"),
    ("/U/journal/2020/12", "/U/journal/2020/11"),
    ("/U/journal/", None),
    ("//", None),
    ("/U/", None),
    ("/", None),
    ("~/journal/2020/12", "~/journal/2020/11")
]


class Test(TestCase):
    def test_get_prior_dir(self):
        for case in prior_dir_cases:
            input_val = case[0]
            expected = case[1]
            actual = journaldir.get_prior_dir(input_val)
            # print("input: {} expected: {}, actual: {}".format(input_val, expected, actual))
            self.assertEqual(expected, actual)


class TestUserPaths(TestCase):

    # Logic change.  Now create dir if it doesn't exist.
    # def testUserJournalPathRaisesE(self):
    #     with self.assertRaises(tlutil.TaskSourceException) as tse:
    #         journaldir.UserPaths("/some/bad/path", "/another/bad/path")
    #     part_of_e_val = tse.exception.value[-31:]
    #     self.assertEqual("for journals is not a directory", part_of_e_val)

    # ok not raising exception.  Endeavor dir is not required.
    # def testUserEndeavorPathRaisesE(self):
    #     with self.assertRaises(journaldir.TaskSourceException) as tse:
    #         journaldir.UserPaths("/", "/another/bad/path")
    #     part_of_e_val = tse.exception.value[-32:]
    #     self.assertEqual("for endeavors is not a directory", part_of_e_val)

    def testUserPathConstructor(self):
        "doesn't really test anything, but can run a asegment of code for debugging"
        # may require JOURNAL_PATH set to run, such as
        #  JOURNAL_PATH=/Users/paulsons/dev/tl2/testuser/testjournal
        user_path_object = journaldir.UserPaths()
        # print(str(user_path_object))
        self.assertEqual("pass", "pass")


unit_test_tmp_dir.DirTree() # initializes dirs and files for testing
upo = tl_testdata.getUnitTestUserPathObject()   #journaldir.UserPaths() # defaults based on environment
test_storydir_str = journaldir.path_join(upo.endeavor_path, "aGoal")

class TestStoryDir(TestCase):
    """
	a StoryDir object represents the directory containing files with task Items
	and names matching journaldir.story_pat.
	"""

    def __init__(self, *args, **kwargs):
        super(TestStoryDir, self).__init__(*args, **kwargs)
        unit_test_tmp_dir.DirTree() # constructor initializes dirs and files for testing

    def testStoryDirConstructor(self):
        """
        constructor creates an object with a list of files.
        This test depends on a particular directory with some stories
        """
        # this is dependant on an Endeavor dir and story dir in the file system.
        #  The unit test suite creates all that.
        expected_storydir_str = f"StoryDir:({test_storydir_str}):{test_storydir_str}/small story.md,{test_storydir_str}/the rest of the work story.md,{test_storydir_str}/an unprioritized story.md"

        sd = journaldir.StoryDir(test_storydir_str)
        # print("sd", sd)
        self.assertEqual(expected_storydir_str, str(sd))

#    def test

class TestFileIO(TestCase):
    """
    # test file i/o
    """
    def testWriteFilePathAndReadFileStr(self):
        """
        verify symmetry between  write_filepath() and  read_file_str()
        :return:
        """
        fileIOPath = journaldir.path_join(upo.endeavor_path, "file-io-test.txt")
        journaldir.write_filepath(tl_testdata.dtask_line, fileIOPath)
        expected_str = journaldir.read_file_str(fileIOPath)
        self.assertEqual(expected_str, tl_testdata.dtask_line)

    def createDirWithFiles(self, dir: str, files: List[str]):
        """

        :param dir: expected to be a creatable path to a directory
        :param files: list of files with no leading path
        :return: dir
        """
        os.makedirs(dir)
        for file in files:
            baseName = os.path.basename(file)
            filePath = os.path.join(dir, baseName)
            Path(filePath).touch()
        return dir

    def cleanUpDirWithFiles(self, dirToRemove: str):
        if os.path.isdir(dirToRemove):
            files = os.listdir(dirToRemove)
            for file in files:
                os.remove(os.path.join(dirToRemove, file))

            os.rmdir(dirToRemove)


    def testMoveFilesAndGetFileNamesByPattern(self):
        """
        Tests move_files() and get_file_names_by_pattern
        Generates some files in a dir, and then moves them by pattern to another dir.
        Test passes if the files in he target dir are the files that matched the original pattern.
        :return:
        """
        tag = "testMoveFilesAndGetFileNamesByPattern"
        try:
            # --- Setup a dir with some file

            fileList = ['SomeFile.txt', 'journal-2021-08-18.md', 'journal-2021-08-19.md', 'journal-2021-08-21.md',
                        'journal-2021-08-22.md', 'journal-2021-08-23.md']
            sourceDir = os.path.join(unit_test_tmp_dir.uttd, "mvFileTestSourceDir")
            destDir = os.path.join(unit_test_tmp_dir.uttd, "mvFileTestDestDir")

            # start clean in case an old failure left some junk there.
            self.cleanUpDirWithFiles(sourceDir)
            self.cleanUpDirWithFiles(destDir)

            dirShouldExistWithFiles = self.createDirWithFiles(sourceDir, fileList)
            os.makedirs(destDir)

            # --- test the funcs that should move the files
            fullyQualifiedSourceMatchFileList = journaldir.get_file_names_by_pattern(sourceDir, apCfg.blotter_pat)
            journaldir.move_files(destDir, fullyQualifiedSourceMatchFileList)
            # print(f"dirShouldExistWithFiles: {dirShouldExistWithFiles}")
            fullyQualifiedDestMatchFileList = journaldir.get_file_names_by_pattern(destDir, apCfg.blotter_pat)
            sourceFileList = [ os.path.basename(sf) for sf in fullyQualifiedSourceMatchFileList]
            destFileList = [ os.path.basename(df) for df in fullyQualifiedDestMatchFileList]
            self.assertCountEqual(sourceFileList, destFileList)

        finally:
            # print(f"Executing the finally clause in {tag}")
            self.cleanUpDirWithFiles(dirShouldExistWithFiles)
            self.cleanUpDirWithFiles(destDir)
