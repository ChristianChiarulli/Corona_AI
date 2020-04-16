from flask import Flask

app = Flask(__name__)

from phue import Bridge
import random


b = Bridge("10.0.0.106")

# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
b.connect()

lights = b.lights

light_list = [l.name for l in lights]

light_dict = {k: v for (k, v) in enumerate(light_list)}


@app.route("/")
def hello_world():
    print(light_dict.get(0))
    return light_dict


if __name__ == "__main__":
    app.run()
