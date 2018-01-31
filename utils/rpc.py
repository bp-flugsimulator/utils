"""
This module contains rpc classes which allowes
rpc via websockets. The command executor is a
client which listens on the websocket.
"""

__all__ = ["ProtocolError", "Rpc"]


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
