from fastapi import FastAPI, WebSocket

from phue import Bridge

b = Bridge("10.0.0.106")

b.connect()

# lights = b.get_light_objects()

# b.get_sensor_objects()


# print(lights)

# import random


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

        if "on" in data_array:
            print("TURNED ON")
            b.set_light("Office Light", "on", True)

        elif "off" in data_array:
            print("TURNED OFF")
            b.set_light("Office Light", "on", False)
        elif "color" in data_array:
            for light in lights:
                b.set_light(light.name, "on", True)
                light.brightness = 254
                light.xy = [random.random(), random.random()]

        print(data)
        await websocket.send_text(f"You said: {data}")
