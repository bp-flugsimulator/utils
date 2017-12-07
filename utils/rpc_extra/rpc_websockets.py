"""
This module holds all classes which depends on websockets.
Since websockets is a optional dependency.
"""
import asyncio
import websockets
import logging

__all__ = ["RpcReceiver"]

from utils import Command, ReceiverError, Rpc, Status


class RpcReceiver:
    """
    Represents a client which connects via websockets to
    a websocket server. This client receives commands
    and executes them.
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
        logging.debug("Got close call ... closing connections.")
        self.closed = True
        try:
            self.sender_session.close()
            self.listen_session.close()
        except:
            pass

    @asyncio.coroutine
    def run(self):
        """
        Listen on a connection and executes the incoming commands,
        if it is a valid command. The result will be send (notified)
        via the send connection.
        """

        logging.debug("Connect to sender.")
        self.sender_session = yield from self.sender_connection
        logging.debug("Connect to listener.")
        self.listen_session = yield from self.listen_connection

        try:
            while not self.closed:
                logging.debug("Listen on command channel.")
                data = yield from self.listen_session.recv()
                try:
                    cmd = Command.from_json(data)
                    logging.debug("Received command {}.".format(cmd))
                    callable_command = Rpc.get(cmd.func)
                    logging.debug("Found correct function ... calling.")
                    res = yield from asyncio.coroutine(callable_command)(
                        **cmd.args)
                    result = Status.ok(res)
                    logging.debug("Function returned {}.".format(result))
                except ReceiverError as err:
                    result = Status.err(str(err))
                    logging.debug("Function returned {}.".format(result))

                yield from self.sender_session.send(result)
        except websockets.exceptions.ConnectionClosed as err:
            logging.error(str(err))
            if err.code != 1000:
                raise err
        finally:
            logging.debug("Closing connections.")
            yield from self.listen_session.close()
            yield from self.sender_session.close()
