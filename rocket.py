from datetime import datetime
import heapq
import threading
class Rocket:
    def __init__(self, id: str, launch_time: str, last_update_time: str, last_message_number: int, 
                 speed: int, rocket_type: str, mission: str):
        self.id: str = id
        self.launch_time: datetime = datetime.fromisoformat(launch_time)
        self.last_update_time: datetime = datetime.fromisoformat(last_update_time)
        self.last_message_number: int = last_message_number
        self.speed: int = speed
        self.rocket_type: str = rocket_type
        self.mission: str = mission
        self.status: str = "Launched"
        self.explosion_reason: str | None = None
        
        # Buffer for messages that arrive out of order
        # Stores tuples of (message_number, original_message_dict)
        self.message_buffer: list[tuple[int, dict]] = []

        # Individual lock for each rocket
        self.lock = threading.RLock()

    def append_message_to_buffer(self, message_number: int, message: dict):
        """Append a message to the buffer."""
        message = (message_number, message)
        # Append to buffer
        heapq.heappush(self.message_buffer, message)

    def pop_message_from_buffer(self):
        """Pop the next message from the buffer."""
        if self.message_buffer:
            heapq.heappop(self.message_buffer)
        
    def increase_speed(self, increment: int, msg_time_str: str, msg_number: int):
        """Increase the speed of the rocket by a given increment."""
        self.speed += increment
        self.update_time_and_message_number(msg_time_str, msg_number)

    def decrease_speed(self, decrement: int, msg_time_str: str, msg_number: int):
        """Decrease the speed of the rocket by a given decrement."""
        self.speed -= decrement
        self.update_time_and_message_number(msg_time_str, msg_number)

    def explode(self, explosion_reason: str, msg_time_str: str, msg_number: int):
        """Set the status of the rocket to 'Exploded' and record the explosion reason."""
        self.status = "Exploded"
        self.explosion_reason = explosion_reason
        self.update_time_and_message_number(msg_time_str, msg_number)

    def update_mission(self, new_mission: str, msg_time_str: str, msg_number: int):
        """Update the mission of the rocket."""
        self.mission = new_mission
        self.update_time_and_message_number(msg_time_str, msg_number)

    def update_time_and_message_number(self, msg_time_str: str, msg_number: int):
        """Update the last update time and message number of the rocket."""
        self.last_update_time = datetime.fromisoformat(msg_time_str)
        self.last_message_number = msg_number

    def to_dict(self) -> dict:
        """Serializes the rocket state to a dictionary for API responses."""
        return {
            "id": self.id,
            "launch_time": self.launch_time,
            "last_update_time": self.last_update_time,
            "last_message_number": self.last_message_number,
            "speed": self.speed,
            "rocket_type": self.rocket_type,
            "mission": self.mission,
            "status": self.status,
            "explosion_reason": self.explosion_reason
        }
