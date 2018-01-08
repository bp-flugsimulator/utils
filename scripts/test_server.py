import logging, sys
import os
import asyncio
import signal
import websockets
import json
import multiprocessing

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

            except Exception as err:
                logging.debug("Error while receiving/removing item.")
                logging.debug(err)
                sys.exit(1)

        @asyncio.coroutine
        def handle_producer(websocket):
            """
            Handles the outgoing messages.
            """
            for elm in send:
                logging.debug("Send element: {}".format(elm))
                yield from websocket.send(elm)

            while True:
                yield from asyncio.sleep(1)

        @asyncio.coroutine
        def handler(websocket, path):
            """
            Forwards all elements in the queue directly into the
            websocket.
            """
            logging.debug("New connection on path {}".format(path))
            if path == "/send_to_server":
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
                handler, host='0.0.0.0', port=8750)
        except Exception as err:
            logging.debug(err)
            sys.exit(1)

        yield from stop

        logging.debug("Received SIGTERM ... closing server.")
        server_handle.close()
        yield from server_handle.wait_closed()

    def handle_stop(signum, frame):
        """
        Handle incoming SIGTERM signals.
        """
        stop.set_result(None)

    loop.run_until_complete(server(stop))


if __name__ == '__main__':

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        COLOR_TEXT + "[SERVER] [%(asctime)s]: %(message)s" + COLOR_END,
        datefmt='%M:%S')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    logging.debug("Fork method: {}".format(multiprocessing.get_start_method()))
    logging.debug("This Process pid: {}".format(os.getpid()))
    logging.debug("Parent Process pid: {}".format(os.getppid()))

    logging.debug("Reading stdin.")
    line = sys.stdin.readline()
    line = line.rstrip()

    try:
        logging.debug("Reading json input.")
        data = json.loads(line)
        i = data['input']
        o = data['output']
    except:
        logging.debug("Error while getting values (input, output).")
        sys.exit(1)

    if not isinstance(i, list):
        logging.debug("Input is not instance of list.")
        sys.exit(1)

    if not isinstance(o, list):
        logging.debug("Input is not instance of list.")
        sys.exit(1)

    run(i, o)
    sys.exit(0)
