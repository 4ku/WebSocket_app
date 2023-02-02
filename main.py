from entities import Client, Server, Agent, Sensor1, Sensor2
import asyncio

# IP address of the host and port number to use
host = "localhost"
port = 5192


# A callback function that will be triggered when data is received to client1
def my_callback1(sensor_id, sensor_readings, my_arg1, my_arg2):
    # Display the ID of the sensor and its readings
    print(f"Received readings from {sensor_id} for client1: {sensor_readings}")
    # Display the values of `my_arg1` and `my_arg2`
    print(f"my_arg1 value: {my_arg1}, my_arg2 value: {my_arg2}\n")


def my_callback2(sensor_id, sensor_readings):
    # Display the ID of the sensor and its readings
    print(f"Sensor: {sensor_id}")
    print(f"Sensor data: {sensor_readings}\n")


async def main():
    # Launch a server
    server = Server(host, port)
    await server.start()

    # Create three sensors
    sensor1 = Sensor1("CE7238J")
    sensor2 = Sensor2("CF9382K")
    sensor3 = Sensor2()

    # Create agents
    agent1 = Agent()
    agent2 = Agent()
    # Connect the agents to the server
    await agent1.connect(host, port)
    await agent2.connect(host, port)
    # Add sensors to the agents
    await agent1.add_sensor(sensor1)
    await agent1.add_sensor(sensor2)
    await agent2.add_sensor(sensor2)
    await agent2.add_sensor(sensor3)

    # Create two clients
    client1 = Client(host, port)
    client2 = Client(host, port)

    # Connect clients to the server
    await client1.connect()
    await client2.connect()

    # Request connection status for a specific sensor
    is_connected = await client1.sensorConnected("CE7238J")
    print("Sensor CE7238J is connected:", is_connected)

    # If the sensor is connected, subscribe to its readings
    if is_connected:
        await client1.subscribe("CE7238J")
        await client2.subscribe("CE7238J")

    # Register the callback functions for the sensors
    await client1.registerCallback("CE7238J", my_callback1, "client1", "sensor1")
    await client2.registerCallback("CE7238J", my_callback2)
    await client1.registerCallback(sensor2.id, my_callback1, "client1", "sensor2")
    await client2.registerCallback(sensor3.id, my_callback2)

    # Start reading data from the sensors
    task1 = asyncio.create_task(agent1.read_sensors())
    task2 = asyncio.create_task(agent2.read_sensors())
    
    task3 = asyncio.create_task(client1.listen())
    task4 = asyncio.create_task(client2.listen())

    try:
        await asyncio.gather(task1, task2, task3, task4)
    except Exception as e:
        print(e)
    finally:
        # Disconnect agents from the server
        await agent1.close()
        # await agent2.close()

        # Unsubscribe from the sensor
        await client1.unsubscribe("CE7238J")

        # Disconnect clients from the server
        await client1.disconnect()
        # await client2.disconnect()

        # Stop the server
        server.stop()

asyncio.run(main())
