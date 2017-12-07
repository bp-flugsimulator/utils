"""
Test file for the rpc module.
"""

import unittest
import asyncio
import signal
import time
import json
import os
import subprocess

import websockets
from utils import Rpc, RpcReceiver, Command, Status

# multiprocessing.set_start_method('spawn')


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
        py = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "server.py")

        return asyncio.create_subprocess_exec(
            py,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )

    def to_json(self):
        return json.dumps({"input": self.send, "output": self.output})


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
    def tets_rpc_multiple_same_name(self):
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
        import logging, sys

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        root.addHandler(ch)

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

        cont = asyncio.Future()
        loop.add_signal_handler(signal.SIGCONT, cont.set_result, None)

        abrt = asyncio.Future()
        loop.add_signal_handler(signal.SIGABRT, abrt.set_result, None)

        server = Server(
            [
                Command("math_add", integer1=1, integer2=2).to_json(),
            ],
            [
                Status.ok(3).to_json(),
            ],
            loop,
        )

        process = loop.run_until_complete(server.run())
        loop.run_until_complete(cont)
        process.stdin.write(server.to_json())

        recv = RpcReceiver(
            'ws://127.0.0.1:8750/receive_from_server',
            'ws://127.0.0.1:8750/send_to_server',
        )

        first = asyncio.ensure_future(recv.run())
        second = asyncio.ensure_future(abrt)
        third = asyncio.ensure_future(server.run())

        @asyncio.coroutine
        def run():
            """
            Wrapper for event loop.
            """
            _, pending = yield from asyncio.wait(
                [
                    first,
                    second,
                    third,
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for pen in pending:
                pen.cancel()

        loop.run_until_complete(run())
        print("Terminate")
        process.terminate()
        print("Wait")
        loop.run_until_complete(process.wait())
        recv.close()


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
