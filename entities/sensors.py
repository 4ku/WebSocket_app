import random
import string
import asyncio

class Sensor:
    """A base class for a Sensor.
    
    Attributes:
        id (str): The id of the sensor.
        data (Any): The data generated by the sensor.
        task (asyncio.Task): The async task to generate data.
    """

    def __init__(self, id: str = None):
        self.data = None
        self.task = asyncio.create_task(self.generate_data())

        if id is None:
            # Generate random ID
            self.id = ''.join(random.choices(
                string.ascii_letters + string.digits, k=7))
        else:
            self.id = id

    async def _create_data(self):
        """Create the data for the sensor.

        This is an abstract method that should be implemented by subclasses.
        """
        raise NotImplementedError

    async def generate_data(self):
        """Generate new data for the sensor every second."""
        while True:
            self.data = await self._create_data()
            await asyncio.sleep(1)

    def has_new_data(self) -> bool:
        """Return True if the sensor has new data, False otherwise."""
        return self.data is not None

    def read(self):
        """Read the data from the sensor and clear it.

        Returns:
            Any: The data generated by the sensor.
        """
        data = self.data
        self.data = None
        return data

class Sensor1(Sensor):
    """A subclass of Sensor that generates random integers."""

    async def _create_data(self) -> int:
        return random.randint(1, 100)

class Sensor2(Sensor):
    """A subclass of Sensor that generates random strings."""

    async def _create_data(self) -> str:
        return ''.join(random.choices(
            string.ascii_letters + string.digits, k=10))
