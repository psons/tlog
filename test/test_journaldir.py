#!/usr/local/bin/python3

import unittest

# tlog stuff
from unittest import TestCase

import testdata
import journaldir


# class Test_get_repos(unittest.TestCase):
#  todo - implement this test
# def testReadFile(self):
# 	repos = journaldir.get_repos()
# 	print(repos)
# 	self.assertEqual("", "")

# class Test_get_file_names(unittest.TestCase):
# 	def testGetFileNames(self):
# 		names = journaldir.get_file_names(testdata.data_dir)
# 		print(names)


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
			print("input: {} expected: {}, actual: {}".format(input_val, expected, actual))
			self.assertEqual(expected, actual)
