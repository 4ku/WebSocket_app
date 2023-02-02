import websockets
import asyncio
import json

class Agent:
    """
    The `Agent` class is used to connect to a websocket and manage sensor objects.
    """
    def __init__(self):
        """
        Initialize an instance of `Agent` by creating an empty list of `sensors`.
        """
        self.sensors = []

    async def connect(self, host: str, port: int):
        """
        Connect to a websocket using the given `host` and `port` number.
        
        :param host: The hostname of the websocket to connect to.
        :type host: str
        :param port: The port number of the websocket to connect to.
        :type port: int
        """
        self.host = host
        self.port = port
        self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
    
    async def send_data(self, sensor, data):
        """
        Send data from a `sensor` to the connected websocket.
        
        :param sensor: The sensor object whose data is to be sent.
        :param data: The sensor readings data to be sent.
        """
        await self.websocket.send(json.dumps({
            "event": "new_sensor_data",
            "data": {
                "sensor_id": sensor.id,
                "sensor_readings": data
            }
        }))
    
    async def add_sensor(self, sensor):
        """
        Add a `sensor` to the list of sensors managed by this `Agent` instance.
        
        :param sensor: The sensor object to be added.
        """
        self.sensors.append(sensor)
        await self.websocket.send(json.dumps({
            "event": "sensor_connect",
            "data": {
                "sensor_id": sensor.id
            }
        }))

    async def read_sensors(self):
        """
        Continuously read data from all connected sensors and send it to the websocket.
        """
        while True:
            for sensor in self.sensors:
                if sensor.has_new_data():
                    data = sensor.read()
                    await self.send_data(sensor, data)
            await asyncio.sleep(0.5)

    async def close(self):
        """
        Close the websocket connection.
        """
        await self.websocket.close()


# This function is used to check the interaction between the agent and the sensors.
async def main():
    from entities.sensors import Sensor1, Sensor2

    host = "localhost"
    port = 5192

    async def handle_client(websocket):
        async for message in websocket:
            print(message)

    await websockets.serve(handle_client, host, port)

    agent = Agent()
    await agent.connect(host, port)
    sensor1 = Sensor1()
    sensor2 = Sensor2()
    await agent.add_sensor(sensor1)
    await agent.add_sensor(sensor2)

    task = asyncio.create_task(agent.read_sensors())
    try:
        await asyncio.gather(task)
    except Exception as e:
        print(e)
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
    