"""
This module holds all classes which depends on websockets. Since websockets is a
optional dependency.
"""
import asyncio
import logging

import websockets

__all__ = ["RpcReceiver"]

from utils import Command, Rpc, Status


class RpcReceiver:
    """
    Represents a client which connects via websockets to a websocket server.
    This client receives commands and executes them (RPC Protocol). It is
    possible to execute async functions. This allows for example to execute sub
    processes without blocking the current process. This specific protocol uses
    two websockets connection. One connection connects to producer. This
    connection receives all commands and adds them to event loop. The other
    connection send the result of the execution. This means it acts as producer.
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
        Returns the URL where the results are send to.

        Returns
        -------
            string
        """
        return self._send

    @property
    def listen(self):
        """
        Returns the URL where the commands are received from.

        Returns
        -------
            string
        """
        return self._listen

    def close(self):
        """
        Closes all connections.
        """

        logging.debug("Got close call ... closing connections.")
        self.closed = True
        try:
            self.sender_session.close()
            self.listen_session.close()
        except:  #pylint: disable=W0702
            pass

    @asyncio.coroutine
    def run(self):
        """
        Listens on the receiver socket and executes the incoming commands. If
        the command is not JSON encoded an Status.err(...) with the exception is
        written to the other socket. Same for failed executions.
        """

        logging.debug("Connect to sender.")
        self.sender_session = yield from self.sender_connection
        logging.debug("Connect to listener.")
        self.listen_session = yield from self.listen_connection

        @asyncio.coroutine
        def handle_message(data):
            cmd = Command.from_json(data)
            logging.debug("Received command {}.".format(cmd.to_json()))
            callable_command = Rpc.get(cmd.method)
            logging.debug("Found correct function ... calling.")

            try:
                res = yield from asyncio.coroutine(callable_command)(
                    **cmd.arguments)

                result = Status.ok(res)
                logging.debug("Function returned {}.".format(result))
            except Exception as err:
                result = Status.err(str(err))
                logging.info("Function raise Exception")

            yield from self.sender_session.send(result.to_json())

        try:
            while not self.closed:
                logging.debug("Listen on command channel.")
                data = yield from self.listen_session.recv()
                asyncio.get_event_loop().create_task(handle_message(data))
        except websockets.exceptions.ConnectionClosed as err:
            logging.error(str(err))
            if err.code != 1000:
                raise err
        finally:
            logging.debug("Closing connections.")
            yield from self.listen_session.close()
            yield from self.sender_session.close()
