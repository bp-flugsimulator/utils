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


class Status:
    """
    Represents a status.
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
            self._status = status
            self._payload = payload

    def __eq__(self, other):
        return self.status() == other.status() and self.payload(
        ) == other.payload()

    def status(self):
        """
        Getter for status.

        Returns
        -------
            string: a status
        """
        return self._status

    def payload(self):
        """
        Getter for payload.

        Returns
        -------
            object: a payload
        """
        return self._payload

    def is_err(self):
        """
        Tests if the current status is an error status.

        Returns
        ------
            boolean
        """
        return self.status() == Status.ID_ERR

    def is_ok(self):
        """
        Tests if the current status is an error status.

        Returns
        ------
            boolean
        """
        return self.status() == Status.ID_OK

    @classmethod
    def ok(cls, val):  #pylint: disable=C0103
        """
        This function creates a status which was
        sucessfull.

        Arguments
        ---------
            val: Any kind of serializable value.
        """
        return cls(cls.ID_OK, val)

    @classmethod
    def err(cls, val):
        """
        This function creates a status which was
        not successful.

        Arguments
        ---------
            val: Any kind of serializable value.
        """
        return cls(cls.ID_ERR, val)

    def to_json(self):
        """
        Generates a json string which holds the information about
        a status.

        Except
        ------
            ProtocolError if the status has no status attribute
            or no result attribute or not message attribute.
            If message and result is set at the same time
            an error will be raised as well.
        """

        data = {self.ID_STATUS: self.status(), self.ID_PAYLOAD: self.payload()}
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

    @staticmethod
    def as_js():
        """
        Returns a javascript class which has the same behavior and names
        like the python class.
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
