import logging, sys
import os
import asyncio
import websockets
import signal
import json


def run(send, incoming):
    """
    Reprensets the process
    """

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[OTHER] %(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    root.addHandler(ch)

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
                incoming.remove(elm)

        @asyncio.coroutine
        def handle_producer(websocket):
            """
            Handles the outgoing messages.
            """
            for elm in send:
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

        try:
            server_handle = yield from websockets.serve(
                handler, '0.0.0.0', 8750)
        except Exception as err:
            print(err)
            sys.exit(1)

        os.kill(os.getppid(), signal.SIGCONT)
        yield from stop

        server_handle.close()
        yield from server_handle.wait_closed()
        loop.stop()

    loop = asyncio.get_event_loop()
    stop = asyncio.Future()

    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.create_task(server(stop))
    loop.run_forever()


if __name__ == '__main__':
    for line in sys.stdin:
        data = json.loads(line)
        try:
            i = data['input']
            o = data['output']
        except Exception as err:
            print(err)
            print("Error while getting values (input, output).")

        if not isinstance(i, list):
            print("Input is not instance of list.")
            sys.exit(1)

        if not isinstance(o, list):
            print("Input is not instance of list.")
            sys.exit(1)

        run(data['input'], data['output'])
