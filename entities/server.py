import json
import websockets
from typing import Dict, Any


class Server:
    """
    A class to represent the server that handles the communication between agents and clients.
    """

    def __init__(self, host: str, port: int):
        """
        Initialize the server instance.

        :param host: The host address to run the server.
        :param port: The port number to run the server.
        """
        self.host = host
        self.port = port
        self.clients = set()  # A set of connected clients.
        # A dictionary to store the connected sensors, with the sensor id as the key and a set of clients that subscribe to the sensor as the value.
        self.sensors = {}

    async def start(self):
        """
        Start the server by running the `websockets.serve` method.
        """
        await websockets.serve(self.handle_messages, self.host, self.port)

    async def handle_agent_message(self, event: str, data: Dict[str, Any]):
        """
        Handle incoming messages from agents.

        :param event: The type of event received from the agent.
        :param data: The data associated with the event.
        """
        if event == "sensor_connect":
            # If a new sensor is connected, add it to the `sensors` dictionary.
            if not data["sensor_id"] in self.sensors:
                self.sensors[data["sensor_id"]] = set()
        elif event == "new_sensor_data":
            # If there is new data from a sensor, send it to all clients that subscribed to the sensor.
            message = json.dumps({
                "event": "new_sensor_data",
                "data": data
            })
            for client in self.sensors[data["sensor_id"]]:
                await client.send(message)

    async def handle_client_message(self, websocket, event: str, data: Dict[str, Any]):
        """
        Handle incoming messages from clients.

        :param websocket: The websocket instance representing the client.
        :param event: The type of event received from the client.
        :param data: The data associated with the event.
        """
        if event == "client_connect":
            # Add the client to the `clients` set when it connects.
            self.clients.add(websocket)
        elif event == "client_disconnect":
            # Remove the client from the `clients` set when it disconnects.
            self.clients.remove(websocket)
        elif event == "sensor_connection_status":
            # Respond to the client with the connection status of a sensor.
            sensor_id = data["sensor_id"]
            connected = sensor_id in self.sensors
            await websocket.send(json.dumps({
                "event": "sensor_connection_status",
                "data": {
                    "sensor_id": sensor_id,
                    "connected": connected
                }
            }))
        elif event == "subscribe_sensor":
            sensor_id = data["sensor_id"]
            if sensor_id in self.sensors:
                self.sensors[sensor_id].add(websocket)
        elif event == "unsubscribe_sensor":
            sensor_id = data["sensor_id"]
            if sensor_id in self.sensors:
                self.sensors[sensor_id].remove(websocket)

    async def handle_messages(self, websocket: websockets.WebSocketServerProtocol):
        """Handles incoming messages from clients or agents.

        This method receives incoming messages and delegates the processing to either `handle_client_message` or
        `handle_agent_message` based on the type of message received.

        Args:
        - websocket (websockets.WebSocketServerProtocol): The websocket connection that received the message.

        """
        async for message in websocket:
            message = json.loads(message)
            event = message["event"]
            data = message.get("data", {})

            await self.handle_agent_message(event, data)
            await self.handle_client_message(websocket, event, data)

    def stop(self):
        """Closes the websocket connection with all clients."""
        for client in self.clients:
            client.close()
