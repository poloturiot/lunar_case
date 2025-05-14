from datetime import datetime

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
        
    def increase_speed(self, increment: int):
        """Increase the speed of the rocket by a given increment."""
        self.speed += increment

    def decrease_speed(self, decrement: int):
        """Decrease the speed of the rocket by a given decrement."""
        self.speed -= decrement

    def explod(self, explosion_reason: str):
        """Set the status of the rocket to 'Exploded' and record the explosion reason."""
        self.status = "Exploded"
        self.explosion_reason = explosion_reason

    def update_mission(self, new_mission: str):
        """Update the mission of the rocket."""
        self.mission = new_mission

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
