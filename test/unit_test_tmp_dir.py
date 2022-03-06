"""
The path is a place that Unit tests can create and clean up subdirectories.
The test runner should set its current working directory to the directory with the project tests.
The parentEndeavor of the directory with the project test should include the following a line with
unit-test-tmp-dir in a .gitignore:


"""
import os

uttd = "../unit-test-tmp-dir"
uttd_exists = os.path.isdir(uttd)