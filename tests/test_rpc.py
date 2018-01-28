"""
Test file for the rpc module.
"""

import unittest
from utils import Rpc, ProtocolError


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
        self.assertRaises(ProtocolError, Rpc.get, "test")

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
    def test_rpc_multiple_same_name(self):  # pylint: disable=R0201
        """
        Test the output for functions with same names.
        """

        class First:  # pylint: disable=R0903,C0111,W0612
            @Rpc.method
            def test(self):
                pass

        class Second:  # pylint: disable=R0903,C0111,W0612
            @Rpc.method
            def test(self):
                pass

    def test_rpc_method_with_uuid_one(self):
        """
        Tests if the element can be found in the method list.
        """

        @Rpc.method_with_uuid
        def test(first):  #pylint: disable=W0613,C0111
            pass

        self.assertIterateEqual(Rpc(), [test])
        self.assertEqual(Rpc.get("test"), test)

    def test_rpc_method_with_uuid_multiple(self):
        """
        Tet the output with multiple functions.
        """

        @Rpc.method
        def test(first):  #pylint: disable=W0613,C0111
            pass

        @Rpc.method_with_uuid
        def test2(uuid):  #pylint: disable=C0111
            pass

        self.assertIterateEqual(Rpc(), [test, test2])
        self.assertEqual(Rpc.get("test"), test)
        self.assertEqual(Rpc.get("test2"), test2)

    @unittest.expectedFailure
    def test_rpc_multiple_same_name_with_uuid(self):  # pylint: disable=R0201
        """
        Test the output for functions with same names.
        """

        class First:  # pylint: disable=R0903,C0111,W0612
            @Rpc.method
            def test(self):
                pass

        class Second:  # pylint: disable=R0903,C0111,W0612
            @Rpc.method_with_uuid
            def test(self):
                pass
