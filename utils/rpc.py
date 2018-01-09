"""
This module contains rpc classes which allowes
rpc via websockets. The command executor is a
client which listens on the websocket.
"""

from uuid import uuid4

import json
__all__ = ["ProtocolError", "Rpc", "Command"]


class ProtocolError(Exception):
    """
    The input/output was not protocol conform.
    """


def method_wrapper(method_list):
    """
    Takes a static argument and returns
    a function which uses this static
    argument.

    Returns
    -------
        A wrapped function which uses a static
        argument, without handing it manually.
    """

    def method_decorator(func):
        """
        A wrapper function for method. Which
        appends the new functions to the internal
        list.
        """
        for fun in method_list:
            if fun.__name__ == func.__name__:
                raise ValueError(
                    "Only functions with unique names are allowed.")

        method_list.append(func)
        return func

    return method_decorator


class Rpc:
    """
    Represents a class which collects all
    RPC methods. Afterwards this class can
    be used to dispatch functions dynamic.
    """
    methods = []
    method = method_wrapper(methods)

    @staticmethod
    def get(func):
        """
        Searches for a function in the internal list.

        Attributes
        ----------
            func: A function identifier

        Returns
        -------
            A function handle if  a function with the given name
            was found. Returns None if no function was found.

        Except
        ------
            ProtocolError the function is unknown
        """
        for method in Rpc.methods:
            if method.__name__ == func:
                return method

        raise ProtocolError("unknown function '{}'".format(func))

    def __iter__(self):
        return self.methods.__iter__()

    @staticmethod
    def clear():
        """
        Removes all element in the method list.
        """
        Rpc.methods.clear()


class Command:
    """
    Represents an rpc call which holds information about the function name and
    arguments. A valid Command is a function name as a string and a dict with
    all function arguments.
    """

    ID_METHOD = 'method'
    ID_ARGUMENTS = 'arguments'
    ID_UUID = 'uuid'

    def __init__(self, method, **kwargs):
        self.__method = method
        self.__arguments = kwargs
        self.__uuid = uuid4().hex

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

            obj = cls(json_data[cls.ID_METHOD], **json_data[cls.ID_ARGUMENTS])
            obj.__uuid = json_data[cls.ID_UUID]
            return obj
        except KeyError as err:
            raise ProtocolError(
                "The given json object has (a) missing key(s). ({})".format(
                    err.args[0]))
