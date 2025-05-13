import datetime

class Rocket:
    def __init__(self, id: str, launch_time: datetime.datetime, last_update_time: datetime.datetime, last_message_number: int, 
                 speed: int, rocket_type: str, mission: str):
        self.id: str = id
        self.launch_time: datetime.datetime = launch_time
        self.last_update_time: datetime.datetime = last_update_time
        self.last_message_number: int = last_message_number
        self.speed: int = speed
        self.rocket_type: str = rocket_type
        self.mission: str = mission
        self.status: str = "Launched"
        self.explosion_reason: str | None = None
        
        # Buffer for messages that arrive out of order (message_number > last_processed_message_number + 1)
        # Stores tuples of (message_number, original_message_dict)
        self.message_buffer: list[tuple[int, dict]] = [] 
        

