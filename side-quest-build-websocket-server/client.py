#!/usr/bin/env python

"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect
import msgpack
import random

async def runClient():
    async with connect("ws://localhost:8765") as websocket:
        # msg = {
        #     'stage': 'prep', 
        #     'type': 'REQUEST', 
        #     'comp': 'cyber'
        # }
        # await websocket.send(json.dumps(msg))
        # message = await websocket.recv()
        # print(message)
        recv_task = asyncio.create_task(incomingMsgHandler(websocket))
        send_task = asyncio.create_task(outgoingMsgHandler(websocket))
    
        await asyncio.gather(recv_task, send_task)

async def incomingMsgHandler(websocket):
    while True:
        packedMsg = await websocket.recv()
        message = msgpack.unpackb(packedMsg, raw=False)
        print(message)


async def outgoingMsgHandler(websocket):
    while True:
        parameter = random.choice(['prep', 'start', 'graph'])
        msg = {
            'stage': parameter,
            'type': 'request'
        }
        await websocket.send(msgpack.packb(msg))
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(runClient())