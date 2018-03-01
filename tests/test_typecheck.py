"""
Tests for module utils.typecheck.
"""
import unittest

from utils.typecheck import ensure_type, ensure_type_array


class TypeCheckTests(unittest.TestCase):
    def test_type_error(self):
        test = "hello world"
        self.assertRaisesRegex(
            TypeError,
            ".*has to be int.*found str",
            ensure_type,
            "test",
            test,
            int,
        )

    def test_type_multi(self):
        test = "hello world"
        ensure_type(
            "test",
            test,
            int,
            str,
        )

    def test_type_success(self):
        test = "hello world"
        ensure_type(
            "test",
            test,
            str,
        )

    def test_type_type_error(self):
        self.assertRaisesRegex(
            ValueError,
            "in.*types is not a type.*found str",
            ensure_type,
            "str",
            "str",
            "str",
        )

    def test_type_array_error(self):
        test = [1, "hello world", 3]

        self.assertRaisesRegex(
            TypeError,
            ".*has to be int.*\n.*index 1 has type str",
            ensure_type_array,
            "test",
            test,
            int,
        )

    def test_type_array_multi(self):
        test = [1, "hello world", 3]

        ensure_type_array(
            "test",
            test,
            int,
            str,
        )

    def test_type_array_success(self):
        test = [1, 2, 3]

        ensure_type_array(
            "test",
            test,
            int,
        )

    def test_type_array_type_error(self):
        self.assertRaisesRegex(
            ValueError,
            "in.*types is not a type.*found str",
            ensure_type_array,
            "str",
            "str",
            "str",
        )
