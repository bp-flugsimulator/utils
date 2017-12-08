"""
Test file for the rpc module.
"""

import unittest
from utils import Rpc, Command


class TestRpc(unittest.TestCase):
    """
    Testcases for the Rpc class.
    """

    def assertIterateEqual(self, first, second):
        """
        Compares two iterable objects if the order of
        the items are the same.
        """
        for first_item, second_item in zip(first, second):
            self.assertEqual(first_item, second_item)

    def setUp(self):
        Rpc.clear()

    def test_rpc_method_one(self):
        """
        Tests if the element can be found in the method list.
        """

        @Rpc.method
        def test(first):  #pylint: disable=W0613,C0111
            pass

        self.assertIterateEqual(Rpc(), [test])
        self.assertEqual(Rpc.get("test"), test)

    def test_rpc_method_none(self):
        """
        Tests the output if none function was given.
        """

        self.assertIterateEqual(Rpc(), [])
        self.assertEqual(Rpc.get("test"), None)

    def test_rpc_multiple(self):
        """
        Tet the output with multiple functions.
        """

        @Rpc.method
        def test(first):  #pylint: disable=W0613,C0111
            pass

        @Rpc.method
        def test2():  #pylint: disable=C0111
            pass

        self.assertIterateEqual(Rpc(), [test, test2])
        self.assertEqual(Rpc.get("test"), test)
        self.assertEqual(Rpc.get("test2"), test2)

    @unittest.expectedFailure
    def test_rpc_multiple_same_name(self):
        """
        Test the output for functions with same names.
        """

        class First:  #pylint: disable=R0903,C0111,W0612
            @Rpc.method
            def test(self):
                pass

        class Second:  #pylint: disable=R0903,C0111,W0612
            @Rpc.method
            def test(self):
                pass


class TestCommand(unittest.TestCase):
    """
    Testcases for the Command class.
    """

    def test_command_with_kwargs(self):
        """
        Uses map arguments.
        """
        cmd = Command("test_func", a=2, b="vier")
        string = '{"command": "test_func", "args": {"a": 2, "b": "vier"}}'
        cmd_string = Command.from_json(string)
        cmd_new = Command.from_json(cmd.to_json())

        self.assertEqual(cmd, cmd_string)
        self.assertEqual(cmd, cmd_new)
        self.assertEqual(cmd_string, cmd_new)

    @unittest.expectedFailure
    def test_command_with_args(self):
        """
        Uses positional arguments, which is not supported.
        """
        Command("test_func", 2, "vier")  #pylint: disable=E1121