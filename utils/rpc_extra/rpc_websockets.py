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

    def __init__(self, url):
        self._url = url

        self._connection = websockets.connect(self.url)
        self._session = None
        tasks = dict()
        self.closed = False

    @property
    def url(self):
        """
        Returns the URL where the results are send to and where the commands are received from.

        Returns
        -------
            string
        """
        return self._url

    @property
    def connection(self):
        """
        Returns the current connection.

        Returns
        -------
            websocket.Connect
        """
        return self._connection

    @property
    def session(self):
        """
        Returns the current session.

        Returns
        -------
            websocket.Session
        """
        return self._session

    def close(self):
        """
        Closes all connections.
        """

        logging.debug("Got close call ... closing connection.")
        self.closed = True
        try:
            self.session.close()
        except Exception as err:  #pylint: disable=W0703
            logging.info('Error while closing websockets.\n%s', str(err))

    @asyncio.coroutine
    def reconnect(self):
        """
        Coroutine that tries to reconnect to self.url 6 times.
        """
        for time in range(6):
            logging.debug('Waiting for %s seconds to reconnect.', pow(2, time))
            yield from asyncio.sleep(pow(2, time))
            try:
                self._connection = websockets.connect(self.url)
                self._session = yield from self.connection
                logging.debug('Successfully reconnected to %s', self.url)
                break
            except ConnectionRefusedError:
                logging.debug('Failed to reconnect to %s.', self.url)

    @asyncio.coroutine
    def run(self):
        """
        Listens on the receiver socket and executes the incoming commands. If
        the command is not JSON encoded an Status.err(...) with the exception is
        written to the other socket. Same for failed executions.
        """

        logging.debug("Opened session on %s.", self.url)
        self._session = yield from self.connection

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

            return Status(status_code, {
                'method': cmd.method,
                'result': result
            }, cmd.uuid)

        try:
            tasks = dict()
            tasks['websocket'] = asyncio.get_event_loop().create_task(
                self.session.recv())

            while not self.closed:
                logging.debug("Listen on command channel.")

                done, _ = yield from asyncio.wait(
                    set(tasks.values()), return_when=asyncio.FIRST_COMPLETED)

                tasks = dict(
                    (k, v) for (k, v) in tasks.items() if not v.done())

                for future in done:
                    data = None
                    try:
                        data = future.result()
                    except websockets.exceptions.ConnectionClosed as err:
                        if err.code != 1000:
                            logging.error('failed to receive message \n%s',
                                          str(err))
                            yield from self.reconnect()
                            tasks['websocket'] = asyncio.get_event_loop(
                            ).create_task(self.session.recv())
                            break
                        else:
                            self.closed = True
                            break

                    logging.debug('Future type: %s', type(data))

                    if isinstance(data, str):
                        cmd = Command.from_json(data)

                        if cmd.uuid in tasks:
                            tasks[cmd.uuid].cancel()
                            logging.debug('Canceled command %s.', cmd.method)
                        else:
                            tasks[cmd.uuid] = asyncio.get_event_loop(
                            ).create_task(execute_call(cmd))
                            logging.debug('Received command %s.',
                                          cmd.to_json())
                        tasks['websocket'] = asyncio.get_event_loop(
                        ).create_task(self.session.recv())
                    if isinstance(data, Status):
                        try:
                            yield from self.session.send(data.to_json())
                        except websockets.exceptions.ConnectionClosed as err:
                            if err.code != 1000:
                                logging.error('failed to send message \n%s',
                                              str(err))
                                yield from self.reconnect()
                                yield from self.session.send(data.to_json())
                            else:
                                self.closed = True

        finally:
            logging.debug("Closing connections.")
            yield from self.session.close()
