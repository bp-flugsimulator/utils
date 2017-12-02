"""
This module contains a status which
can be encoded into a json string.
"""
import json

__all__ = ["FormatError", "Status"]


class FormatError(Exception):
    """
    The given data are not valid encoded.
    """

    def __init__(self, message):
        super(FormatError).__init__(self)
        self.message = message


class Status:
    """
    Represents a status.
    """

    ID_OK = "ok"
    ID_ERR = "err"
    ID_STATUS = "status"
    ID_PAYLOAD = "payload"

    def __init__(self):
        self.status = None
        self.payload = None

    @classmethod
    def ok(cls, val):
        """
        This function creates a status which was
        sucessfull.

        Arguments
        ---------
            val: Any kind of serializable value.
        """
        status = cls()
        status.status = cls.ID_OK
        status.payload = val

        return status

    @classmethod
    def err(cls, val):
        """
        This function creates a status which was
        not sucessfull.

        Arguments
        ---------
            val: Any kind of serializable value.
        """
        status = cls()
        status.status = cls.ID_ERR
        status.payload = val

        return status

    def to_json(self):
        """
        Generates a json string which holds the information about
        a status.

        Except
        ------
            ProtocolError if the status has no status attribute
            or no result attribute or not message attribute.
            If message and result is set at the same time
            an error will be raised aswell.
        """

        data = {self.ID_STATUS: self.status, self.ID_PAYLOAD: self.payload}
        return json.dumps(data)

    @classmethod
    def from_json(cls, data):
        """
        Tries to create a status from a response.

        Attributes
        ----------
            data: a string which is json encoded

        Returns
        -------
            A valid Status

        Except
        ------
            ProtocolError when a key is not found.
        """
        json_data = json.loads(data)

        try:
            status = json_data[cls.ID_STATUS]

            if status == cls.ID_OK:
                return cls.ok(json_data[cls.ID_PAYLOAD])
            elif status == cls.ID_ERR:
                return cls.err(json_data[cls.ID_PAYLOAD])
            else:
                raise FormatError("Missing status field in Status.")

        except KeyError as err:
            raise FormatError("Missing field in encode string. ({})".format(
                err.args[0]))