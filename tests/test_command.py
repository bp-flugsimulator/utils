"""
Test file for the command module
"""

import unittest
from utils import Command, ProtocolError


class TestCommand(unittest.TestCase):
    """
    Testcases for the Command class.
    """

    def test_command_with_kwargs(self):
        """
        Uses map arguments.
        """
        cmd = Command("test_func", a=2, b="vier")
        string = '{{"{}": "test_func", "{}": {{"a": 2, "b": "vier" }}, "{}": "{}"}}'.format(
            Command.ID_METHOD, Command.ID_ARGUMENTS, Command.ID_UUID, cmd.uuid)
        cmd_string = Command.from_json(string)
        cmd_new = Command.from_json(cmd.to_json())

        self.assertEqual(cmd, cmd_string)
        self.assertEqual(cmd, cmd_new)
        self.assertEqual(cmd_string, cmd_new)

    @unittest.expectedFailure
    def test_command_with_args(self):  # pylint: disable=R0201
        """
        Uses positional arguments, which is not supported.
        """
        Command("test_func", 2, "vier")  #pylint: disable=E1121

    def test_command_from_json_ProtocolError_args(self):
        """
        Expects ProtocolError from from_json if args is not a dictionary
        """
        string = '{{"{}": "test_func", "{}": 2 }}'.format(
            Command.ID_METHOD,
            Command.ID_ARGUMENTS,
        )
        self.assertRaises(ProtocolError, Command.from_json, string)

    def test_command_from_json_ProtocolError_command(self):
        """
        Expects ProtocolError from from_json if command is not a string
        """
        string = '{{"{}": 2, "{}": {{"a": 2, "b": "vier"}}}}'.format(
            Command.ID_METHOD,
            Command.ID_ARGUMENTS,
        )
        self.assertRaises(ProtocolError, Command.from_json, string)

    def test_command_from_json_KeyError(self):
        """
        Expects KeyError from from_json if either command or args is missing
        """
        string = '{{"{}": {{"a": 2, "b": "vier"}}}}'.format(
            Command.ID_ARGUMENTS)
        self.assertRaises(ProtocolError, Command.from_json, string)

    def test_command_from_json_uuid_no_string(self):
        """
        Expects ValueError from from_json if the uuid is no str
        """
        string = '{{"{}": "name", "{}": {{"a": "drei", "b": "vier"}}, "{}":2}}'.format(
            Command.ID_METHOD, Command.ID_ARGUMENTS, Command.ID_UUID)
        self.assertRaises(ProtocolError, Command.from_json, string)
