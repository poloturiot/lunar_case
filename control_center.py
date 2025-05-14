import threading
from rocket import Rocket


class ControlCenter:
    def __init__(self):
        self.rockets_fleet: dict[str, Rocket] = {}
        self.lock = threading.Lock()

    def process_incoming_message(self, message: any):
        print(message)

        metadata = message.get("metadata", {})
        payload = message.get("message", {})

        channel_id = metadata.get("channel")
        msg_number = metadata.get("messageNumber")
        msg_type = metadata.get("messageType")
        msg_time_str = metadata.get("messageTime")

        if not all([channel_id, isinstance(msg_number, int), msg_type, msg_time_str]):
            print(f"Error: Invalid message structure: {message}")
            return
        
        with self.lock: # CRITICAL SECTION START
    
            rocket = self.rockets_fleet.get(channel_id)

            # If rocket doesn't exist yet, and it is being Launched add it
            if not rocket and msg_type == "RocketLaunched":
                rocket = Rocket(
                    id=channel_id, 
                    launch_time = metadata.get("messageTime"), 
                    last_update_time = metadata.get("messageTime"), 
                    last_message_number= metadata.get("messageNumber"),
                    speed = payload.get("launchSpeed"),
                    rocket_type = payload.get("type"),
                    mission = payload.get("mission")
                )

                self.rockets_fleet[channel_id] = rocket
            
            if not rocket:
                print(f"[{channel_id}] No rocket found and message is not RocketLaunched ({msg_type}). Cannot process yet.")
                return
            
