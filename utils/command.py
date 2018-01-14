"""
This module contains classes which represent a send command which gets send
over a websocket
"""

import json
from uuid import uuid4
from .rpc import ProtocolError

__all__ = ["Command"]


class Command:
    """
    Represents an rpc call which holds information about the function name and
    arguments. A valid Command is a function name as a string and a dict with
    all function arguments.
    """

    ID_METHOD = 'method'
    ID_ARGUMENTS = 'arguments'
    ID_UUID = 'uuid'

    def __init__(self, method, uuid=None, **kwargs):
        self.__method = method
        self.__arguments = kwargs
        if uuid is None:
            self.__uuid = uuid4().hex
        else:
            self.__uuid = uuid

    def __eq__(self, other):
        return self.method == other.method and self.arguments == other.arguments

    def __iter__(self):
        for key, val in vars(Command).items():
            if isinstance(val, property):
                yield (key, self.__getattribute__(key))

    @property
    def method(self):
        """
        Getter for the name of the method.

        Returns
        -------
            A string which identifies the method.
        """
        return self.__method

    @property
    def arguments(self):
        """
        Getter for the argument dictionary.

        Returns
        -------
            A dictionary of arguments.
        """
        return self.__arguments

    @property
    def uuid(self):
        """
        Getter for uuid.

        Returns
        -------
            A hex value representing a universally unique identifier
        """
        return self.__uuid

    @uuid.setter
    def uuid(self, uuid):
        """
        Setter for __uuid.

        Argument
        --------
        uuid: str
            A hex value representing a universally unique identifier
        """
        self.__uuid = uuid

    def to_json(self):
        """
        Formats the method into a json string.

        Returns
        -------
            A json string.
        """
        return json.dumps(dict(self))

    @classmethod
    def from_json(cls, data):
        """
        Tries to parse a json object from the given data
        and tries to map the json entries to a valid command.

        Attributes
        ----------
            data: a string which is json encoded

        Returns
        -------
            A valid Command

        Except
        ------
            ProtocolError when a key is not found or
            an entire has a wrong type.
        """
        json_data = json.loads(data)
        try:
            if not isinstance(json_data[cls.ID_ARGUMENTS], dict):
                raise ProtocolError("Args has to be a dictionary.")

            if not isinstance(json_data[cls.ID_METHOD], str):
                raise ProtocolError("Method has to be a string.")

            if not isinstance(json_data[cls.ID_UUID], str):
                raise ProtocolError("UUID has to be a string.")

            return cls(
                method=json_data[cls.ID_METHOD],
                uuid=json_data[cls.ID_UUID],
                **json_data[cls.ID_ARGUMENTS])
        except KeyError as err:
            raise ProtocolError(
                "The given json object has (a) missing key(s). ({})".format(
                    err.args[0]))
