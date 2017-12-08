"""
Test file for rpc websockets.
"""

import unittest
import asyncio
import signal
import json
import os
import sys
import logging
import multiprocessing

import websockets
from utils import Rpc, RpcReceiver, Command, Status
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

COLOR_TEXT = '\033[35m'
COLOR_END = '\033[0m'


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
        """
        Returns the subprocess handler.abs

        Returns
        -------
            process
        """
        py_file = os.path.join(
            os.path.join(os.getcwd(), "scripts"), "test_server.py")
        logging.debug("Running python script {} as server.".format(py_file))

        return asyncio.create_subprocess_shell(
            "{} {}".format(sys.executable, py_file),
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    def to_json(self):
        """
        Transforms the test set into json.

        Returns
        -------
            A string which is json formatted.
        """
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

        logging.debug("Fork method: {}".format(
            multiprocessing.get_start_method()))
        logging.debug("This Process pid: {}".format(os.getpid()))

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

        if os.name == 'nt':
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
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
        logging.debug("This Process pid: {}".format(os.getpid()))

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
