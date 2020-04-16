import asyncio
import websockets


async def hello():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:

        await websocket.send("MESSAGE")

        greeting = await websocket.recv()
        print(f"< {greeting}")


asyncio.get_event_loop().run_until_complete(hello())


