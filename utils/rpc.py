"""
This module contains rpc classes which allowes
rpc via websockets. The command executor is a
client which listens on the websocket.
"""

import json
__all__ = ["ReceiverError", "ProtocolError", "Rpc", "Command"]


class ReceiverError(Exception):
    """
    An error occured while the executon.
    This error should be used inside the
    RPC function, which is identified by
    the @Rpc.method.
    """

    def __init__(self, message):
        super(ReceiverError).__init__(self)
        self.message = message


class ProtocolError(Exception):
    """
    The input/output was not protocol conform.
    """

    def __init__(self, message):
        super(ProtocolError).__init__(self)
        self.message = message


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
    Represents a class wich collects all
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

        """
        for method in Rpc.methods:
            if method.__name__ == func:
                return method
        return None

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
    Represents an rpc call which holds information
    about the function namen and arugments.
    A valid Command is a funcion name as a string
    and a dict with all function arguments.
    """

    ID_COMMAND = 'command'
    ID_ARGS = 'args'

    def __init__(self, func, **kwargs):
        self.func = func
        self.args = kwargs

    def __eq__(self, other):
        return self.func == other.func and self.args == other.args

    def to_json(self):
        """
        Formats the command into a json string.

        Returns
        -------
            A json string.
        """
        data = {self.ID_COMMAND: self.func, self.ID_ARGS: self.args}
        return json.dumps(data)

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
            an entrie has a wrong type.
        """
        json_data = json.loads(data)
        try:
            if not isinstance(json_data[cls.ID_ARGS], dict):
                raise ProtocolError("Args has to be a dictionary.")

            if not isinstance(json_data[cls.ID_COMMAND], str):
                raise ProtocolError("Command has to be a string.")

            for key in json_data[cls.ID_ARGS].keys():
                if not isinstance(key, str):
                    raise ProtocolError("Wrong format for key in arguments.")

            return cls(json_data[cls.ID_COMMAND], **json_data[cls.ID_ARGS])
        except KeyError as err:
            raise ProtocolError(
                "The given json object has (a) missing key(s). ({})".format(
                    err.args[0]))
