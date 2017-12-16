"""
This module contains a status which
can be encoded into a json string.
"""
import json

__all__ = ["FormatError", "Status"]


class FormatError(Exception):
    """
    The input data is not valid encoded.
    """


class Status:
    """
    Represents a status which is returned by a method. If the method was
    successful it should return Status.ok(...) if not Status.err(...).
    Status holds a playload which can be any kind of data. This payload
    is related to the status. This means if Status.err(...) is returned
    the payload should contain information about the causes of the failure.
    """

    ID_OK = "ok"
    ID_ERR = "err"
    ID_STATUS = "status"
    ID_PAYLOAD = "payload"

    def __init__(self, status, payload):
        if status != Status.ID_OK and status != Status.ID_ERR:
            raise ValueError(
                "Status only accept a string with `{}` or `{}`".format(
                    Status.ID_OK, Status.ID_ERR))
        else:
            self.__status = status
            self.__payload = payload

    def __eq__(self, other):
        return self.status == other.status and self.payload == other.payload

    def __iter__(self):
        for key, val in vars(Status).items():
            if isinstance(val, property):
                yield (key, self.__getattribute__(key))

    @property
    def status(self):
        """
        Returns the raw status string of this instance. Using this function is
        not recommended. Use is_ok or is_err for checking the status.

        Returns
        -------
            string: a status
        """
        return self.__status

    @property
    def payload(self):
        """
        Returns the playload of this instance.

        Returns
        -------
            object: a payload
        """
        return self.__payload

    def is_err(self):
        """
        Checks if the current status is Status.err(...).

        Returns
        ------
            boolean
        """
        return self.status == Status.ID_ERR

    def is_ok(self):
        """
        Checks if the current status is Status.ok(...).

        Returns
        ------
            boolean
        """
        return self.status == Status.ID_OK

    @classmethod
    def ok(cls, payload):  #pylint: disable=C0103
        """
        Creates an instance of this class with a payload and a successful status
        string. DO NOT use json.dumps(...) as a payload unless you want the
        payload to be a string and not a json object.

        Arguments
        ---------
            payload: Any kind of serializable value.
        """
        return cls(cls.ID_OK, payload)

    @classmethod
    def err(cls, payload):
        """
        Creates an instance of this class with a payload and a unsuccessful
        status string. DO NOT use json.dumps(...) as a payload unless you want
        the payload to be a string and not a json object.


        Arguments
        ---------
            payload: Any kind of serializable value.
        """
        return cls(cls.ID_ERR, payload)

    def to_json(self):
        """
        Generates a string which is json encoded. This string can be send via
        network and decoded to a json object by the receiver.

        Except
        ------
            ProtocolError if the status has no status attribute
            or no result attribute or not message attribute.
            If message and result is set at the same time
            an error will be raised as well.
        """
        return json.dumps(dict(self))

    @classmethod
    def from_json(cls, data):
        """
        Tries to parse a json object from a json encoded string.
        The resulting json object is mapped to Status.

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

    @staticmethod
    def as_js():
        """
        Returns a javascript class which has the same behavior and names like
        the python class.

        Returns
        -------
            string: which contains a valid javascript class
        """
        return """
            class Status {{
                constructor (status, payload) {{
                    if (status != "{id_ok}" && status != "{id_err}") {{
                        throw new TypeError("Status only accept a string with `{id_ok}` or `{id_err}`..");
                    }} else {{
                        this._{id_status} = status;
                        this._{id_payload} = payload;
                    }}
                }}

                equals(other) {{
                    return this.{id_status} == other.{id_status} &&
                        this.{id_payload} == other.{id_payload};
                }}

                get status() {{
                    return this._{id_status};
                }}

                get payload() {{
                    return this._{id_payload};
                }}

                is_ok() {{
                    return this.{id_status} == "{id_ok}";
                }}

                is_err() {{
                    return this.{id_status} == "{id_err}";
                }}

                static ok(payload) {{
                    return new Status("{id_ok}", payload);
                }}

                static err(payload) {{
                    return new Status("{id_err}", payload);
                }}

                to_json() {{
                    return JSON.stringify({{ "{id_status}": this.status, "{id_payload}": this.payload }});
                }}

                static from_json(data) {{
                    var json = JSON.parse(data);
                    return new Status(json["{id_status}"], json["{id_payload}"]);
                }}
            }}
        """.format(
            id_ok=Status.ID_OK,
            id_err=Status.ID_ERR,
            id_status=Status.ID_STATUS,
            id_payload=Status.ID_PAYLOAD,
        )
