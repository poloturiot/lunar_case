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
                    launch_time = msg_time_str, 
                    last_update_time = msg_time_str, 
                    last_message_number= metadata.get("messageNumber"),
                    speed = payload.get("launchSpeed"),
                    rocket_type = payload.get("type"),
                    mission = payload.get("mission")
                )
                
                # Add rocket to fleet
                self.rockets_fleet[channel_id] = rocket

                print(f"Rocket {channel_id} added to fleet.")

            if not rocket:
                print(f"[{channel_id}] No rocket found and message is not RocketLaunched ({msg_type}). Cannot process yet.")
                return
            
            if msg_type == "RocketSpeedIncreased":
                rocket = self.rockets_fleet[channel_id]
                speed_increment = payload.get("by")
                rocket.increase_speed(speed_increment)
                rocket.last_update_time = msg_time_str
                rocket.last_message_number = msg_number
                print(f"[{channel_id}] Speed increased by {speed_increment}. New speed: {rocket.speed}.")

            if msg_type == "RocketSpeedDecreased":
                rocket = self.rockets_fleet[channel_id]
                speed_decrement = payload.get("by")
                rocket.decrease_speed(speed_decrement)
                rocket.last_update_time = msg_time_str
                rocket.last_message_number = msg_number
                print(f"[{channel_id}] Speed decreased by {speed_decrement}. New speed: {rocket.speed}.")
            
            if msg_type == "RocketExploded":
                rocket = self.rockets_fleet[channel_id]
                reason = payload.get("reason")
                rocket.explod(reason)
                rocket.last_update_time = msg_time_str
                rocket.last_message_number = msg_number
                print(f"[{channel_id}] Rocket exploded. Reason: {reason}.")

            if msg_type == "RocketMissionChanged":
                rocket = self.rockets_fleet[channel_id]
                new_mission = payload.get("newMission")
                rocket.update_mission(new_mission)
                rocket.last_update_time = msg_time_str
                rocket.last_message_number = msg_number
                print(f"[{channel_id}] Mission changed to {new_mission}.")