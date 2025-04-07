import asyncio
import queue
from functools import partial

import msgpack
from websockets.asyncio.server import serve


async def handle_webapp_communication(
    websocket, wsCommToSimThreadQ, simThreadToWsCommQ
):
    print(wsCommToSimThreadQ, simThreadToWsCommQ)
    recv_task = asyncio.create_task(
        websocket_recv_handler(websocket, wsCommToSimThreadQ, simThreadToWsCommQ)
    )
    send_task = asyncio.create_task(
        websocket_send_handler(websocket, wsCommToSimThreadQ, simThreadToWsCommQ)
    )

    await asyncio.gather(recv_task, send_task)


async def websocket_recv_handler(websocket, wsCommToSimThreadQ, simThreadToWsCommQ):
    async for message in websocket:
        incoming_message = msgpack.unpackb(message, raw=False)
        handleIncomingMessage(incoming_message, wsCommToSimThreadQ, simThreadToWsCommQ)


def handleIncomingMessage(message, wsCommToSimThreadQ, simThreadToWsCommQ):
    stage = message["stage"]

    if stage == "start":
        handleStartSim(message, wsCommToSimThreadQ, simThreadToWsCommQ)
    elif stage == "stop":
        handleStopSim(message)
    elif stage == "changeGraphs":
        handlePrepMessage(message)
    elif stage == "getGraph":
        handleGetGraphRequest(message)


def handleStartSim(message, wsCommToSimThreadQ, simThreadToWsCommQ):
    print("Starting sim...")
    print(message)
    wsCommToSimThreadQ.put(message)


def handleStopSim(message):
    print("Stopping sim...")
    print(message)


def handlePrepMessage(message):
    print("Handling the prep msg...")
    print(message)


def handleChangeGraphs(message):
    print("Changing the graphs")
    print(message)


def handleGetGraphRequest(message):
    print("Handling the get graph request")
    print(message)


async def websocket_send_handler(websocket, wsCommToSimThreadQ, simThreadToWsCommQ):
    while True:
        msg = {}
        await websocket.send(msgpack.packb(msg))
        await asyncio.sleep(5)


async def wsServerInit(wsCommToSimThreadQ, simThreadToWsCommQ):
    handle_webapp_communication_with_params = partial(
        handle_webapp_communication,
        wsCommToSimThreadQ=wsCommToSimThreadQ,
        simThreadToWsCommQ=simThreadToWsCommQ,
    )

    async with serve(
        handle_webapp_communication_with_params, "localhost", 8765
    ) as server:
        await server.serve_forever()


def startWsServer(wsCommToSimThreadQ: queue, simThreadToWsCommQ: queue):
    asyncio.run(wsServerInit(wsCommToSimThreadQ, simThreadToWsCommQ))
