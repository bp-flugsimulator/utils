"""
Testcases for path.py module.
"""
import unittest
import os

from utils.path import remove_trailing_path_seperator


class PathTests(unittest.TestCase):
    def test_remove_trailing(self):
        path = "/home/user/test/"
        self.assertEqual("", os.path.basename(path))
        self.assertEqual(
            "test",
            os.path.basename(remove_trailing_path_seperator(path)),
        )

    def test_remove_trailing_no_remove(self):
        path = "/home/user/test"
        self.assertEqual("test", os.path.basename(path))
        self.assertEqual(
            "test",
            os.path.basename(remove_trailing_path_seperator(path)),
        )

    def test_remove_trailing_empty(self):
        path = ""
        self.assertEqual("", os.path.basename(path))
        self.assertEqual(
            "",
            os.path.basename(remove_trailing_path_seperator(path)),
        )
