import asyncio
import json
import websockets
import datetime
import time
CONNECTIONS = []

async def hello(websocket):
    CONNECTIONS.append(websocket)
    
    print(CONNECTIONS)
    while True:
        b_message = await websocket.recv()
        if b_message:
            message = json.loads(b_message)
            print(f'Server Received: {message}')
            if message.get("message"):
                data = {"name":message.get("name", ""), "message":message.get("message"), "time": time.mktime(datetime.datetime.utcnow().timetuple())}
                print(data)
                greeting = json.dumps(data)
                print(greeting)
                websockets.broadcast(CONNECTIONS, greeting)

async def main():
    
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()  # run forever

