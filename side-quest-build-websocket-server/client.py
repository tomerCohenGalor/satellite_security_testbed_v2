#!/usr/bin/env python

"""Client using the asyncio API."""

import asyncio
import random

import msgpack
from websockets.asyncio.client import connect

tle = {
    "tle": [
        "PROGRESS-MS 26",
        "1 58961U 24029A   24213.90256772  .00036721  00000+0  66014-3 0  9994",
        "2 58961  51.6377  93.7862 0005973 147.7965 320.0621 15.49475947 25767",
    ]
}

attacks = {
    "attacks": [
        {"duration": "10", "occurrence": "2,8,16,40,45", "name": "HeaterUp"},
        {"duration": "50", "occurrence": "2,77,81", "name": "malUP"},
    ]
}

time = {"time": [2024, 7, 31, 20, 17, 55.0]}

min_max = {"min": 1369.7478539121023, "max": 1369.8887229789696}


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
        parameter = random.choice(["prep", "start", "getGraph"])
        msg = {
            "stage": parameter, 
            "type": "request",
            "data": {}
            }
        if parameter == "start":
            msg["data"].update(tle)
            msg["data"].update(attacks)
            msg["data"].update(time)
            msg["data"].update(min_max)
        await websocket.send(msgpack.packb(msg))
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(runClient())
