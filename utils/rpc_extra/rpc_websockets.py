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
        except Exception as err:  #pylint: disable=W0703
            logging.info('Error while closing websockets.\n%s', str(err))

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
        def execute_call(cmd):
            """
            Handles an incoming message in a seperat task
            """
            callable_command = Rpc.get(cmd.method)
            logging.debug("Found correct function ... calling.")

            try:
                result = yield from asyncio.coroutine(callable_command)(
                    **cmd.arguments)
                status_code = Status.ID_OK
                logging.debug(
                    'method %s with args: %s returned %s.',
                    cmd.method,
                    cmd.arguments,
                    result,
                )
            except Exception as err:  # pylint: disable=W0703
                result = str(err)
                status_code = Status.ID_ERR
                logging.info('Function raise Exception(%s)', result)

            return Status(status_code,
                          {'method': cmd.method,
                           'result': result}, cmd.uuid)

        try:
            tasks = dict()
            tasks['websocket'] = asyncio.get_event_loop().create_task(
                self.listen_session.recv())

            while not self.closed:
                logging.debug("Listen on command channel.")

                (done, _) = yield from asyncio.wait(
                    set(tasks.values()), return_when=asyncio.FIRST_COMPLETED)

                tasks = dict(
                    (k, v) for (k, v) in tasks.items() if not v.done())

                for future in done:
                    data = future.result()
                    logging.debug('Future type: %s', type(future.result()))

                    if isinstance(data, str):
                        cmd = Command.from_json(data)

                        if cmd.method == '':
                            if cmd.uuid in tasks:
                                tasks.pop(cmd.uuid).cancel()
                                status = Status(Status.ID_OK, {'method': ''},
                                                cmd.uuid)
                                logging.debug('Canceled command with uuid %s.',
                                              cmd.uuid)
                            else:
                                status = Status(Status.ID_ERR, {'method': ''},
                                                cmd.uuid)
                                logging.error(
                                    "Can't cancel unknown command %s",
                                    cmd.uuid)

                            yield from self.sender_session.send(
                                status.to_json())
                            tasks['websocket'] = asyncio.get_event_loop(
                            ).create_task(self.listen_session.recv())

                        else:
                            logging.debug('Received command %s.',
                                          cmd.to_json())
                            tasks[cmd.uuid] = asyncio.get_event_loop(
                            ).create_task(execute_call(cmd))
                            tasks['websocket'] = asyncio.get_event_loop(
                            ).create_task(self.listen_session.recv())

                    if isinstance(data, Status):
                        yield from self.sender_session.send(data.to_json())

        except websockets.exceptions.ConnectionClosed as err:
            logging.error('failed to send/receive message \n%s', str(err))
            if err.code != 1000:
                raise err
        finally:
            logging.debug("Closing connections.")
            yield from self.listen_session.close()
            yield from self.sender_session.close()
