"""
This module holds all classes which depdends on websockets.
Since websockets is a optional dependency.
"""
import asyncio
import websockets

__all__ = ["RpcReceiver"]

from utils import Command, ReceiverError, Rpc, Status


class RpcReceiver:
    """
    Represents a client which connects via websockets to
    a websocket server. This client receives commands
    and excutes them.
    """

    def __init__(self, listen, send):
        self._listen = listen
        self._send = send

        self.listen_connection = websockets.connect(self.listen)
        self.sender_connection = websockets.connect(self.send)
        self.sender_session = None
        self.listen_session = None
        self.closed = False

    @property
    def send(self):
        """
        Returns the url on which this client send
        it's notifications.

        Returns
        -------
            A given url.
        """
        return self._send

    @property
    def listen(self):
        """
        Returns the url on which this client listens on.

        Returns
        -------
            A given url.
        """
        return self._listen

    def close(self):
        """
        Close the connections to the servers.
        """
        self.closed = True
        self.sender_session.close()
        self.listen_session.close()

    @asyncio.coroutine
    def run(self, callback):
        """
        Listens to the specified address and reads the stream.
        If a package was received it will be encoded and tried
        to executed. The send stream and the result will be
        pushed into the callback function.

        Arguments
        ---------
            callback: a function witch takes a send stream and a result
            stop: a event which is called when a signal received

        """
        self.sender_session = yield from self.sender_connection
        self.listen_session = yield from self.listen_connection

        try:
            while not self.closed:
                data = yield from self.listen_session.recv()
                try:
                    cmd = Command.from_json(data)
                    callable_command = Rpc.get(cmd.func)
                    res = yield from asyncio.coroutine(callable_command)(
                        **cmd.args)
                    result = Status.ok(res)
                except ReceiverError as err:
                    result = Status.err(str(err))

                yield from callback(self.sender_session, result)

        except websockets.exceptions.ConnectionClosed as err:
            if err.code != 1000:
                raise err
        finally:
            yield from self.listen_session.close()
            yield from self.sender_session.close()
