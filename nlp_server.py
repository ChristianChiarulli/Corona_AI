from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.get("/")
async def get():
    return "app is up"


@app.websocket("/ws")
async def display_voice(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        data_array = data.split()

        print(data)

        await websocket.send_text(f"You said: {data}")
