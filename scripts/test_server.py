"""
This module contains a rpc server used for testing.
"""

import logging
import sys
import os
import asyncio
import json
import multiprocessing
import websockets

COLOR_TEXT = '\033[34m'
COLOR_END = '\033[0m'


def run(send, incoming):
    """
    Represents the process
    """
    loop = asyncio.get_event_loop()
    stop = asyncio.Future()

    @asyncio.coroutine
    def server(stop):
        """
        Arguments
        ---------
            stop: @coroutine which signals that the server should stop

        Represents a process which the websockets
        server runs on.
        """

        @asyncio.coroutine
        def handle_consumer(websocket):
            """
            Handles the incoming messages.
            """
            try:
                while True:
                    logging.debug("Wait for messages.")
                    elm = yield from websocket.recv()
                    logging.debug("Received element.")
                    incoming.remove(elm)
                    logging.debug("Removed element.")

                    if not incoming:
                        break

            except Exception as err:  # pylint: disable=W0703
                logging.debug("Error while receiving/removing item.")
                logging.debug(err)
                sys.exit(1)

        @asyncio.coroutine
        def handle_producer(websocket):
            """
            Handles the outgoing messages.
            """
            for elm in send:
                logging.debug('Send element: %s', elm)
                yield from websocket.send(elm)

            while True:
                yield from asyncio.sleep(1)

        @asyncio.coroutine
        def handler(websocket, path):
            """
            Forwards all elements in the queue directly into the
            websocket.
            """
            logging.debug('New connection on path %s', path)
            if path == '/send_to_server':
                yield from handle_consumer(websocket)
            elif path == "/receive_from_server":
                yield from handle_producer(websocket)
            else:
                ValueError("path not registered.")

            if not incoming:
                stop.set_result(None)

        try:
            logging.debug("Starting websocket server.")
            server_handle = yield from websockets.serve(
                handler, host='127.0.0.1', port=8750)
        except Exception as err:  #pylint: disable=W0703
            logging.debug(err)
            sys.exit(1)

        yield from stop

        logging.debug("Received SIGTERM ... closing server.")
        server_handle.close()
        yield from server_handle.wait_closed()

    loop.run_until_complete(server(stop))


if __name__ == '__main__':

    ROOT = logging.getLogger()
    ROOT.setLevel(logging.DEBUG)

    CHANNEL_HANDLER = logging.StreamHandler(sys.stdout)
    CHANNEL_HANDLER.setLevel(logging.DEBUG)
    FORMATTER = logging.Formatter(
        COLOR_TEXT + "[SERVER] [%(asctime)s]: %(message)s" + COLOR_END,
        datefmt='%M:%S')
    CHANNEL_HANDLER.setFormatter(FORMATTER)
    ROOT.addHandler(CHANNEL_HANDLER)

    logging.debug('Fork method: %s', multiprocessing.get_start_method())
    logging.debug('This Process pid: %d', os.getpid())
    logging.debug('Parent Process pid: %d', os.getppid())

    logging.debug("Reading stdin.")
    LINE = sys.stdin.readline()
    LINE = LINE.rstrip()

    try:
        logging.debug("Reading json input.")
        DATA = json.loads(LINE)
        INPUT = DATA['input']
        OUTPUT = DATA['output']
    except Exception as err:  # pylint: disable=W0703
        logging.debug("Error while getting values (input, output).\n%s",
                      str(err))
        sys.exit(1)

    if not isinstance(INPUT, list):
        logging.debug("Input is not instance of list.")
        sys.exit(1)

    if not isinstance(OUTPUT, list):
        logging.debug("Input is not instance of list.")
        sys.exit(1)

    run(INPUT, OUTPUT)
    sys.exit(0)
