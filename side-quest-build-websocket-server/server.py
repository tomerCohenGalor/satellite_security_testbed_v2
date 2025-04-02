import asyncio
from websockets.asyncio.server import serve
import msgpack
import websocket

async def runServer(websocket):
    recv_task = asyncio.create_task(websocket_recv_handler(websocket))
    send_task = asyncio.create_task(websocket_send_handler(websocket))
    
    await asyncio.gather(recv_task, send_task)

async def websocket_recv_handler(websocket):
    async for message in websocket:
        incoming_message = msgpack.unpackb(message, raw=False)
        handleIncomingMessage(incoming_message)

def handleIncomingMessage(message):
    stage = message['stage']

    if stage == 'start':
        handleStartSim(message)
    elif stage == 'stop':
        handleStopSim(message)
    elif stage == 'prep':
        handlePrepMessage(message)
    elif stage == 'changeGraphs':
        handlePrepMessage(message)
    elif stage == 'getGraph':
        handleGetGraphRequest(message)

def handleStartSim(message):
    print("Starting sim...")
    print(message)

def handleStopSim(message):
    print("Stopping sim...")
    print(message)

def handlePrepMessage                                                                                                                                                                                                                 (message):
    print("Handling the prep msg...")
    print(message)

def handleChangeGraphs(message):
    print("Changing the graphs")
    print(message)

def handleGetGraphRequest(message):
    print("Handling the get graph request")
    print(message)

async def websocket_send_handler(websocket):
    while True:
        msg = {}
        await websocket.send(msgpack.packb(msg))
        await asyncio.sleep(5)



async def main():
    async with serve(runServer, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())