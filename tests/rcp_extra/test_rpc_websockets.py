"""
Test file for rpc websockets.
"""

import asyncio
import json
import logging
import multiprocessing
import os
import signal
import sys
import time
import unittest

import websockets

from utils import Command, Rpc, RpcReceiver, Status

# is on both platforms available

COLOR_TEXT = '\033[35m'
COLOR_END = '\033[0m'


class Server:
    """
    Represents a test server which runs a websocket and
    a set of sendable items and a set of items which
    should be received.
    """

    def __init__(self, send, output):
        self.send = send
        self.output = output

    def run(self):
        """
        Returns the subprocess handler.abs

        Returns
        -------
            process
        """

        if os.name == 'nt':
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        logging.debug("Fork method: {}".format(
            multiprocessing.get_start_method()))
        logging.debug("This Process pid: {}".format(os.getpid()))
        py_file = os.path.join(
            os.path.join(os.getcwd(), "scripts"), "test_server.py")
        logging.debug("Running python script {} as server.".format(py_file))
        logging.debug("using {} to execute server.".format(sys.executable))

        raw_process = asyncio.create_subprocess_exec(
            sys.executable,
            py_file,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            loop=loop,
        )

        logging.debug("Start child process.")
        process = loop.run_until_complete(raw_process)
        logging.debug("Child process spawned with pid {}".format(process.pid))
        logging.debug("This Process pid: {}".format(os.getpid()))

        logging.debug("Writing json object to stdin.")
        # transfer test set to process
        process.stdin.write(self.to_json().encode())
        process.stdin.write("\n".encode())

        # run instant in background
        asyncio.ensure_future(forward_stream_to(process.stdout, sys.stdout))
        asyncio.ensure_future(forward_stream_to(process.stderr, sys.stdout))

        time.sleep(1)

        recv = RpcReceiver(
            'ws://127.0.0.1:8750/receive_from_server',
            'ws://127.0.0.1:8750/send_to_server',
        )

        @asyncio.coroutine
        def wait_for_end():
            """
            Wrapper for event loop.
            """
            finished, pending = yield from asyncio.wait(
                [
                    asyncio.ensure_future(recv.run()),
                    asyncio.ensure_future(process.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            logging.debug("wait_for_end() -> finished")
            for fin in finished:
                if fin.exception() is not None:
                    try:
                        raise fin.exception()
                    except websockets.exceptions.ConnectionClosed as err:
                        if err.code == 1001:
                            pass
                        else:
                            raise err
                    except Exception as err:
                        raise err

                if fin.result == 1:
                    raise ValueError("Program return EXIT_FAILURE")

            for pen in pending:
                pen.cancel()

        logging.debug("Running main loop.")
        loop.run_until_complete(wait_for_end())
        recv.close()
        logging.debug("Send SIGTERM to child process.")
        process.terminate()
        logging.debug("Wait for process to close.")
        loop.run_until_complete(process.wait())

    def to_json(self):
        """
        Transforms the test set into json.

        Returns
        -------
            A string which is json formatted.
        """
        return json.dumps({"input": self.send, "output": self.output})


class CloseFailServer(Server):
     def run(self):
        """
        Returns the subprocess handler.abs

        Returns
        -------
            process
        """

        if os.name == 'nt':
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        logging.debug("Fork method: {}".format(
            multiprocessing.get_start_method()))
        logging.debug("This Process pid: {}".format(os.getpid()))
        py_file = os.path.join(
            os.path.join(os.getcwd(), "scripts"), "test_server.py")
        logging.debug("Running python script {} as server.".format(py_file))
        logging.debug("using {} to execute server.".format(sys.executable))

        raw_process = asyncio.create_subprocess_exec(
            sys.executable,
            py_file,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            loop=loop,
        )

        logging.debug("Start child process.")
        process = loop.run_until_complete(raw_process)
        logging.debug("Child process spawned with pid {}".format(process.pid))
        logging.debug("This Process pid: {}".format(os.getpid()))

        logging.debug("Writing json object to stdin.")
        # transfer test set to process
        process.stdin.write(self.to_json().encode())
        process.stdin.write("\n".encode())

        # run instant in background
        asyncio.ensure_future(forward_stream_to(process.stdout, sys.stdout))
        asyncio.ensure_future(forward_stream_to(process.stderr, sys.stdout))

        time.sleep(1)

        recv = RpcReceiver(
            'ws://127.0.0.1:8750/receive_from_server',
            'ws://127.0.0.1:8750/send_to_server',
        )

        @asyncio.coroutine
        def wait_for_end():
            """
            Wrapper for event loop.
            """
            finished, pending = yield from asyncio.wait(
                [
                    asyncio.ensure_future(recv.run()),
                    asyncio.ensure_future(process.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            logging.debug("wait_for_end() -> finished")
            for fin in finished:
                if fin.exception() is not None:
                    try:
                        raise fin.exception()
                    except websockets.exceptions.ConnectionClosed as err:
                        if err.code == 1001:
                            pass
                        else:
                            raise err
                    except Exception as err:
                        raise err

                if fin.result == 1:
                    raise ValueError("Program return EXIT_FAILURE")

            for pen in pending:
                pen.cancel()

        logging.debug("Running main loop.")
        #loop.run_until_complete(wait_for_end())
        recv.close()
        logging.debug("Send SIGTERM to child process.")
        process.terminate()
        logging.debug("Wait for process to close.")
        loop.run_until_complete(process.wait())



@asyncio.coroutine
def forward_stream_to(source, destination):
    """
    Forwards all lines from the source to
    the destination.

    Arguments
    ---------
        source: Source stream
        destination: Destination stream

    Returns
    -------
        None
    """
    while True:
        try:
            line = yield from source.readline()
            if not line:
                break
            destination.write(line.decode())
        except:
            pass

    return None


class TestRpcReceiver(unittest.TestCase):
    """
    Testcases for the RpcReceiver class.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            COLOR_TEXT + "[CLIENT] [%(asctime)s]: %(message)s" + COLOR_END,
            datefmt='%M:%S',
        )
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def setUp(self):
        Rpc.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        asyncio.get_event_loop().close()

    def test_math_add_async(self):
        """
        Testing simple math add function with async features.
        """

        @Rpc.method
        @asyncio.coroutine
        def math_add(integer1, integer2):
            """
            Simple add function with async.

            Arguments
            ---------
                integer1: first operand
                integer2: second operand
            """
            yield from asyncio.sleep(1)
            res = (integer1 + integer2)
            return res

        server = Server(
            [
                Command("math_add", integer1=1, integer2=2).to_json(),
            ],
            [
                Status.ok(3).to_json(),
            ],
        ).run()

    def test_math_add(self):
        """
        Testing simple math add function with async features.
        """

        @Rpc.method
        def math_add(integer1, integer2):
            """
            Simple add function with async.

            Arguments
            ---------
                integer1: first operand
                integer2: second operand
            """
            res = (integer1 + integer2)
            return res

        server = Server(
            [
                Command("math_add", integer1=1, integer2=2).to_json(),
            ],
            [
                Status.ok(3).to_json(),
            ],
        ).run()


    def test_error_close(self):
        """
        Tests if RPC-Receiver doesnt raise an exception its closed early.
        """

        @Rpc.method
        @asyncio.coroutine
        def math_add(integer1, integer2):
            """
            Simple add function with async.

            Arguments
            ---------
                integer1: first operand
                integer2: second operand
            """
            res = (integer1 + integer2)
            return res

        server = CloseFailServer(
            [
                Command("math_add", integer1=1, integer2=2).to_json(),
            ],
            [
                Status.ok(3).to_json(),
            ],
        ).run()