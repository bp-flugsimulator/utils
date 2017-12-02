"""
Test file for the rpc module.
"""

import unittest
import asyncio
import signal
import websockets
import time
import os

from multiprocessing import Process
from utils.rpc import Rpc, RpcReceiver, Command
from utils.status import Status


class Server:
    def __init__(self, send, output):
        self.send = send
        self.output = output

        self.process = None

    def __enter__(self):
        def process():
            """
            Reprensets the process
            """

            @asyncio.coroutine
            def server(stop):
                """

                Arguments
                ---------
                    stop: @coroutine which signals that the server should stop
                Represents a proces which the websockets
                server runs on.
                """

                @asyncio.coroutine
                def handle_consumer(websocket):
                    """
                    Handles the incomming messages.
                    """
                    while True:
                        elm = yield from websocket.recv()
                        self.output.remove(elm)

                @asyncio.coroutine
                def handle_producer(websocket):
                    """
                    Handles the outgoing messages.
                    """
                    for elm in self.send:
                        yield from websocket.send(elm)

                    while True:
                        pass

                @asyncio.coroutine
                def handler(websocket, path):
                    """
                    Forwards all elements in the queue directly into the
                    websocket.
                    """
                    if path == "/send_to_server":
                        yield from handle_consumer(websocket)
                    elif path == "/receive_from_server":
                        yield from handle_producer(websocket)
                    else:
                        ValueError("path not registered.")

                server_handle = yield from websockets.serve(
                    handler, '0.0.0.0', 8750)
                os.kill(os.getppid(), signal.SIGCONT)
                yield from stop
                server_handle.close()
                yield from server_handle.wait_closed()

            loop = asyncio.get_event_loop()
            stop = asyncio.Future()

            print(os.getpid())

            def debug():
                print("TERM")

            loop.add_signal_handler(signal.SIGTERM, debug)
            loop.run_until_complete(server(stop))

        self.process = Process(target=process)
        self.process.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.kill(self.process.pid, signal.SIGTERM)
        print(self.process.pid)
        print("term")
        self.process.join()
        print("joined")


class TestRpc(unittest.TestCase):
    """
    Testcases for the Rpc class.
    """

    def setUp(self):
        Rpc.clear()

    def test_rpc_method_one(self):
        """
        Tests if the element can be found in the method list.
        """

        @Rpc.method
        def test(first):
            pass

        for (x, y) in zip(Rpc(), [test]):
            self.assertEqual(x, y)

        self.assertEqual(Rpc.get("test"), test)

    def test_rpc_method_none(self):
        """
        Tests the output if none function was given.
        """

        for (x, y) in zip(Rpc(), []):
            self.assertEqual(x, y)

        self.assertEqual(Rpc.get("test"), None)

    def test_rpc_multiple(self):
        """
        Tet the output with multiple functions.
        """

        @Rpc.method
        def test(first):
            pass

        @Rpc.method
        def test2():
            pass

        for (x, y) in zip(Rpc(), [test, test2]):
            self.assertEqual(x, y)

        self.assertEqual(Rpc.get("test"), test)
        self.assertEqual(Rpc.get("test2"), test2)

    @unittest.expectedFailure
    def tets_rpc_multiple_same_name(self):
        """
        Test the output for functions with the same name
        """

        class First:
            @Rpc.method
            def test(self):
                pass

        class Second:
            @Rpc.method
            def test(self):
                pass


class TestRpcReceiver(unittest.TestCase):
    """
    Testcases for the RpcReceiver class.
    """

    def test_math_add(self):
        pass
        # """
        # Testing simple math add function.
        # """

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
        pass
        # stop = asyncio.Future()
        # start = asyncio.Future()

        # @Rpc.method
        # @asyncio.coroutine
        # def math_add(integer1, integer2):
        #     """
        #     Simple add function with async.

        #     Arguments
        #     ---------
        #         integer1: first operand
        #         integer2: second operand
        #     """
        #     yield from asyncio.sleep(1)
        #     res = (integer1 + integer2)
        #     return res

        # @asyncio.coroutine
        # def callback(sender, item):
        #     """
        #     Simple callback
        #     """
        #     yield from sender.send(item.to_json())
        #     stop.set_result(None)

        # server = Server(
        #     [
        #         Command("math_add", integer1=1, integer2=2).to_json(),
        #     ],
        #     [
        #         Status.ok(3).to_json(),
        #     ],
        # )

        # loop = asyncio.get_event_loop()
        # loop.add_signal_handler(signal.SIGCONT, start.set_result, None)

        # with server:
        #     print("waiting for server")
        #     asyncio.wait(start)
        #     print("ready")
        #     time.sleep(0.5)
        #     print("ready")

        #     recv = RpcReceiver(
        #         'ws://127.0.0.1:8750/receive_from_server',
        #         'ws://127.0.0.1:8750/send_to_server',
        #     )

        #     first = asyncio.ensure_future(recv.run(callback))
        #     second = asyncio.ensure_future(stop)

        #     @asyncio.coroutine
        #     def run():
        #         """
        #         Wrapper for event loop.
        #         """
        #         _, pending = yield from asyncio.wait(
        #             [first, second],
        #             return_when=asyncio.FIRST_COMPLETED,
        #         )
        #         for pen in pending:
        #             pen.cancel()

        #     loop.run_until_complete(run())
        #     recv.close()


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
        self.assertEqual(cmd.to_json(), string)

    @unittest.expectedFailure
    def test_command_with_args(self):
        """
        Uses positional arguments, which is not supported.
        """
        Command("test_func", 2, "vier")
