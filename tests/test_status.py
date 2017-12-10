"""
Test file for the status module.
"""

import unittest
from utils.status import Status, FormatError


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
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    def test_ok_with_array_of_strings(self):
        """
        Testcase with simple array of string.
        """
        status = Status.ok(["Hello World", "Bye"])
        string = '{"status": "ok", "payload": ["Hello World", "Bye"]}'
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    def test_ok_with_array_of_integer(self):
        """
        Testcase with simple array of integer.
        """
        status = Status.ok([0, 1, 2, 3])
        string = '{"status": "ok", "payload": [0, 1, 2, 3]}'
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    def test_ok_with_map_mixed(self):
        """
        Testcase with map with mixed objects.
        """
        status = Status.ok({"Hello World": "Bye", "Integer": 0})
        string = '{"status": "ok", "payload": {"Hello World": "Bye", "Integer": 0}}'
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    def test_err_with_string(self):
        """
        Testcase with simple string.
        """
        status = Status.err("Hello World")
        string = '{"status": "err", "payload": "Hello World"}'
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    def test_err_with_array_of_strings(self):
        """
        Testcase with simple array of string.
        """
        status = Status.err(["Hello World", "Bye"])
        string = '{"status": "err", "payload": ["Hello World", "Bye"]}'
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    def test_err_with_array_of_integer(self):
        """
        Testcase with simple array of integer.
        """
        status = Status.err([0, 1, 2, 3])
        string = '{"status": "err", "payload": [0, 1, 2, 3]}'
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    def test_err_with_map_mixed(self):
        """
        Testcase with map with mixed objects.
        """
        status = Status.err({"Hello World": "Bye", "Integer": 0})
        string = '{"status": "err", "payload": {"Hello World": "Bye", "Integer": 0}}'
        status_string = Status.from_json(string)
        status_new = Status.from_json(status.to_json())

        self.assertEqual(status, status_string)
        self.assertEqual(status, status_new)
        self.assertEqual(status_string, status_new)

    @unittest.expectedFailure
    def test_ok_with_no_serializable(self):
        """
        Testcase wich failes because the input object is not
        serializable.
        """
        status = Status.ok(ValueError("This is a value error."))
        status.to_json()

    @unittest.expectedFailure
    def test_err_with_no_serializable(self):
        """
        Testcase which failes because the input object is not
        serializable.
        """
        status = Status.err(ValueError("This is a value error."))
        status.to_json()

    def test_status_init_value_error(self):
        """
        Testcase which tests for a ValueError in status.__init__
        """
        self.assertRaises(ValueError, Status.__init__, None, "", "")

    def test_from_json_no_status(self):
        """
        Testcase which tests for a FormatError during construction from a 
        json object without a status field
        """
        self.assertRaises(FormatError, Status.from_json, '{"status":""}')

    def test_from_json_key_error(self):
        """
        Tests if an FormatError gets thrown if the json object has a
        missing field
        """
        self.assertRaises(FormatError, Status.from_json, '{}')

    def test_status_is_ok(self):
        """
        Tests if a status that has no error returns true on
        is_ok()
        """
        self.assertTrue(Status(Status.ID_OK, "").is_ok())

    def test_status_is_err(self):
        """
        Tests if a status that contains an error returns true on
        is_err()
        """
        self.assertTrue(Status(Status.ID_ERR, "").is_err())
