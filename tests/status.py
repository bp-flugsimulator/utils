"""
Test file for the status module.
"""

import unittest
from utils.status import Status


class TestStatus(unittest.TestCase):
    """
    Test cases for the class Status.
    """

    def test_ok_with_string(self):
        """
        Testcase with simple string.
        """
        status = Status.ok("Hello World")
        string = '{"status": "ok", "payload": "Hello World"}'
        self.assertEqual(status.to_json(), string)

    def test_ok_with_array_of_strings(self):
        """
        Testcase with simple array of string.
        """
        status = Status.ok(["Hello World", "Bye"])
        string = '{"status": "ok", "payload": ["Hello World", "Bye"]}'
        self.assertEqual(status.to_json(), string)

    def test_ok_with_array_of_integer(self):
        """
        Testcase with simple array of integer.
        """
        status = Status.ok([0, 1, 2, 3])
        string = '{"status": "ok", "payload": [0, 1, 2, 3]}'
        self.assertEqual(status.to_json(), string)

    def test_ok_with_map_mixed(self):
        """
        Testcase with map with mixed objects.
        """
        status = Status.ok({"Hello World": "Bye", "Integer": 0})
        string = '{"status": "ok", "payload": {"Hello World": "Bye", "Integer": 0}}'
        self.assertEqual(status.to_json(), string)

    @unittest.expectedFailure
    def test_ok_with_no_serializable(self):
        """
        Testcase wich failes because the input object is not
        serializable.
        """
        status = Status.ok(ValueError("This is a value error."))
        status.to_json()
