import json
import websockets


class Client:
    """
    Client class provides functionality to interact with the server using websockets. 
    It has methods to connect, disconnect, subscribe and unsubscribe to/from a sensor,
    register and remove callbacks for sensor data, and listen for new sensor data.
    """

    def __init__(self, host: str, port: int):
        """
        Initializes a new instance of the `Client` class with the given host and port.

        :param host: Host name or IP address of the server.
        :type host: str
        :param port: Port number to connect to the server.
        :type port: int
        """
        self.host = host
        self.port = port
        self.sensor_callbacks = {}
        self.websocket = None

    async def connect(self) -> None:
        """
        Connects to the server and sends a `client_connect` event.
        """
        self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
        await self.send_message(json.dumps({
            "event": "client_connect",
            "data": ""
        }))

    async def send_message(self, message) -> None:
        message_sent = False
        while not message_sent:
            try:
                await self.websocket.send(message)
                message_sent = True
            except websockets.ConnectionClosed:
                print("Connection closed, trying to reconnect...")
                await self.connect()

    async def disconnect(self) -> None:
        """
        Disconnects from the server and sends a `client_disconnect` event.
        """
        await self.send_message(json.dumps({
            "event": "client_disconnect",
            "data": ""
        }))
        await self.websocket.close()

    async def sensorConnected(self, sensor_id: str) -> bool:
        """
        Checks if the given sensor is connected to the server.

        :param sensor_id: ID of the sensor to check the connection status for.
        :type sensor_id: str
        :return: `True` if the sensor is connected, `False` otherwise.
        :rtype: bool
        """
        while True:
            try:
                await self.send_message(json.dumps({
                    "event": "sensor_connection_status",
                    "data": {
                        "sensor_id": sensor_id
                    }
                }))
                response = json.loads(await self.websocket.recv())
                return response["data"]["connected"]
            except websockets.ConnectionClosed:
                print("Connection closed, trying to reconnect...")
                await self.connect()

    async def subscribe(self, sensor_id: str) -> None:
        """
        Subscribes to the given sensor.

        :param sensor_id: ID of the sensor to subscribe to.
        :type sensor_id: str
        """
        await self.send_message(json.dumps({
            "event": "subscribe_sensor",
            "data": {
                "sensor_id": sensor_id
            }
        }))

    async def unsubscribe(self, sensor_id: str) -> None:
        """
        Unsubscribes from the given sensor.

        :param sensor_id: ID of the sensor to unsubscribe from.
        :type sensor_id: str
        """
        await self.send_message(json.dumps({
            "event": "unsubscribe_sensor",
            "data": {
                "sensor_id": sensor_id
            }
        }))

    async def registerCallback(self, sensor_id: str, callback, *callback_args):
        """
        Registers a callback for the given sensor, whenever the server sends readings for this sensor, the provided 
        callback will be executed.

        Parameters:
        sensor_id (str): id of the sensor to subscribe to
        callback (callable): callable object to be executed whenever a new reading is received
        *callback_args (optional): extra arguments to be passed to the callback function

        Returns:
        None
        """
        self.sensor_callbacks[sensor_id] = (callback, callback_args)
        await self.subscribe(sensor_id)

    async def removeCallback(self, sensor_id: str):
        """
        Removes the registered callback for a given sensor.

        Parameters:
        sensor_id (str): id of the sensor for which the callback is to be removed

        Returns:
        None
        """
        del self.sensor_callbacks[sensor_id]
        await self.unsubscribe(sensor_id)

    async def listen(self):
        """
        Listens for incoming data from the server and invokes the registered callback for the respective sensor.

        Returns:
        None
        """
        while True:
            try:
                response = json.loads(await self.websocket.recv())
                if response["event"] == "new_sensor_data":
                    sensor_id = response["data"]["sensor_id"]
                    if sensor_id in self.sensor_callbacks:
                        callback, callback_args = self.sensor_callbacks[sensor_id]
                        readings = response["data"]["sensor_readings"]
                        callback(sensor_id, readings, *callback_args)
            except websockets.ConnectionClosed:
                print("Connection closed, trying to reconnect...")
                await self.connect()
