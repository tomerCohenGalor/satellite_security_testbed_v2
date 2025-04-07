import asyncio
import queue
import threading
import time

import msgpack
from utils.simExecutionUtil import handle_simulation_execution
from utils.webAppComUtil import startWsServer
from websockets.asyncio.server import serve

if __name__ == "__main__":
    wsCommToSimThread = queue.Queue()
    simThreadToWsComm = queue.Queue()

    ws_thread = threading.Thread(
        target=startWsServer, args=(wsCommToSimThread, simThreadToWsComm)
    )
    sim_handle_thread = threading.Thread(
        target=handle_simulation_execution, args=(wsCommToSimThread, simThreadToWsComm)
    )

    ws_thread.start()
    sim_handle_thread.start()

    while True:
        time.sleep(1)

    # startWsServer(wsCommToSimThread, simThreadToWsComm)
    # handle_simulation_execution(wsCommToSimThread, simThreadToWsComm)
