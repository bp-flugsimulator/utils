"""
Test file for the rpc module.
"""

import unittest
import asyncio
import signal
import time
import json
import os
import sys
import subprocess
import logging

import websockets
from utils import Rpc, RpcReceiver, Command, Status

COLOR_TEXT = '\033[35m'
COLOR_END = '\033[0m'

try:
    CS_END = signal.SIGTERM
except:
    CS_END = 10

try:
    CS_CONT = signal.SIGCONT
except:
    CS_CONT = 11

try:
    CS_ABORT = signal.SIGABRT
except:
    CS_ABORT = 12


class Server:
    """
    Represents a test server which runs a websocket and
    a set of sendable items and a set of items which
    should be received.
    """

    def __init__(self, send, output, loop):
        self.send = send
        self.output = output
        self.loop = loop
        self.process = None

    def run(self):
        py_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "../scripts/test_server.py")
        logging.debug("Running python script {} as server.".format(py_file))

        return asyncio.create_subprocess_shell(
            "python {}".format(py_file),
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    def to_json(self):
        return json.dumps({"input": self.send, "output": self.output})


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


class TestRpc(unittest.TestCase):
    """
    Testcases for the Rpc class.
    """

    def assertIterateEqual(self, first, second):
        """
        Compares two iterable objects if the order of
        the items are the same.
        """
        for first_item, second_item in zip(first, second):
            self.assertEqual(first_item, second_item)

    def setUp(self):
        Rpc.clear()

    def test_rpc_method_one(self):
        """
        Tests if the element can be found in the method list.
        """

        @Rpc.method
        def test(first):  #pylint: disable=W0613,C0111
            pass

        self.assertIterateEqual(Rpc(), [test])
        self.assertEqual(Rpc.get("test"), test)

    def test_rpc_method_none(self):
        """
        Tests the output if none function was given.
        """

        self.assertIterateEqual(Rpc(), [])
        self.assertEqual(Rpc.get("test"), None)

    def test_rpc_multiple(self):
        """
        Tet the output with multiple functions.
        """

        @Rpc.method
        def test(first):  #pylint: disable=W0613,C0111
            pass

        @Rpc.method
        def test2():  #pylint: disable=C0111
            pass

        self.assertIterateEqual(Rpc(), [test, test2])
        self.assertEqual(Rpc.get("test"), test)
        self.assertEqual(Rpc.get("test2"), test2)

    @unittest.expectedFailure
    def test_rpc_multiple_same_name(self):
        """
        Test the output for functions with same names.
        """

        class First:  #pylint: disable=R0903,C0111,W0612
            @Rpc.method
            def test(self):
                pass

        class Second:  #pylint: disable=R0903,C0111,W0612
            @Rpc.method
            def test(self):
                pass


class TestRpcReceiver(unittest.TestCase):
    """
    Testcases for the RpcReceiver class.
    """

    def test_math_add(self):
        """
        Testing simple math add function.
        """
        pass

        # @Rpc.method
        # def math_add(integer1, integer2):
        #     """
        #     Simple add function without async.

        #     Arguments
        #     ---------
        #         integer1: first operand
        #         integer2: second operand
        #     """
        #     return integer1 + integer2

        # def callback(item):
        #     """
        #     Simple callback
        #     """
        #     self.put(item)

        # RpcReceiver('127.0.0.1').run(callback)

    def test_math_add_async(self):
        """
        Testing simple math add function with async features.
        """
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

        logging.debug("This Process: {}".format(os.getpid()))

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

        loop = asyncio.get_event_loop()

        # server is ready
        cont = asyncio.Future()

        def handle_cont(signum, frame):
            """
            Handles incoming signals.
            """
            cont.set_result(None)

        signal.signal(CS_CONT, handle_cont)

        # server error occurred
        abrt = asyncio.Future()

        def handle_abrt(signum, frame):
            """
            Handles incoming signals.
            """
            abrt.set_result(None)

        signal.signal(CS_ABORT, handle_abrt)

        # server is finished
        end = asyncio.Future()

        def handle_end(signum, frame):
            """
            Handles incoming signals.
            """
            end.set_result(None)

        signal.signal(CS_END, handle_end)

        # define test set
        server = Server(
            [
                Command("math_add", integer1=1, integer2=2).to_json(),
            ],
            [
                Status.ok(3).to_json(),
            ],
            loop,
        )

        logging.debug("Start child process.")
        process = loop.run_until_complete(server.run())
        logging.debug("Child process spawned with pid {}".format(process.pid))

        logging.debug("Writing json object to stdin.")
        # transfer test set to process
        process.stdin.write(server.to_json().encode())
        process.stdin.write("\n".encode())

        # run instant in background
        asyncio.ensure_future(forward_stream_to(process.stdout, sys.stdout))
        asyncio.ensure_future(forward_stream_to(process.stderr, sys.stdout))

        @asyncio.coroutine
        def wait_for_continue():
            """
            Wrapper for event loop.
            """
            finished, pending = yield from asyncio.wait(
                [
                    asyncio.ensure_future(cont),
                    asyncio.ensure_future(process.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            logging.debug("wait_for_cont() -> finished")
            for fin in finished:
                if fin.result == 1:
                    raise ValueError(
                        "Found a result which is not None. That means the process ended which is not wanted in this stage."
                    )

                if fin.result == 0:
                    raise ValueError("Program exited.")

            for pen in pending:
                pen.cancel()

        logging.debug("Wait for SIGCONT.")
        loop.run_until_complete(wait_for_continue())
        logging.debug("Received SIGCONT.")

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
                    asyncio.ensure_future(abrt),
                    asyncio.ensure_future(end),
                    asyncio.ensure_future(process.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            logging.debug("wait_for_end() -> finished")
            for fin in finished:
                if fin.exception() is not None:
                    raise fin.exception()

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


class TestCommand(unittest.TestCase):
    """
    Testcases for the Command class.
    """

    def test_command_with_kwargs(self):
        """
        Uses map arguments.
        """
        cmd = Command("test_func", a=2, b="vier")
        string = '{"command": "test_func", "args": {"a": 2, "b": "vier"}}'
        cmd_string = Command.from_json(string)
        cmd_new = Command.from_json(cmd.to_json())

        self.assertEqual(cmd, cmd_string)
        self.assertEqual(cmd, cmd_new)
        self.assertEqual(cmd_string, cmd_new)

    @unittest.expectedFailure
    def test_command_with_args(self):
        """
        Uses positional arguments, which is not supported.
        """
        Command("test_func", 2, "vier")  #pylint: disable=E1121
