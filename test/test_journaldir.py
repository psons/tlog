#!/usr/local/bin/python3

import unittest

#tlog stuff
import testdata
import journaldir

# class Test_get_repos(unittest.TestCase):
	#  todo - implement this test
	# def testReadFile(self):
	# 	repos = journaldir.get_repos()
	# 	print(repos)
	# 	self.assertEqual("", "")

class Test_get_file_names(unittest.TestCase):
	def testGetFileNames(self):
		names = journaldir.get_file_names(testdata.data_dir)
		print(names)
if __name__ == '__main__':
	unittest.main()
