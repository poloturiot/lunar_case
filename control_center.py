import threading
from rocket import Rocket


class ControlCenter:
    def __init__(self):
        self.rockets_fleet: dict[str, Rocket] = {}
        self.lock = threading.Lock()

    def process_incoming_message(self, message: any):
        """
        Processes incoming messages from the API server.
        """

        metadata = message.get("metadata", {})
        payload = message.get("message", {})

        channel_id = metadata.get("channel")
        msg_number = metadata.get("messageNumber")
        msg_type = metadata.get("messageType")
        msg_time_str = metadata.get("messageTime")

        if not all([channel_id, isinstance(msg_number, int), msg_type, msg_time_str]):
            print(f"Error: Invalid message structure: {message}")
            return
        
        with self.lock:
    
            rocket = self.rockets_fleet.get(channel_id)

            # If rocket doesn't exist yet, and it is being Launched, and should be added to the fleet
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
                rocket.message_buffer.append((msg_number, message))
                return

            if msg_number <= rocket.last_message_number:
                print(f"[{channel_id}] Message number {msg_number} is less than or equal to last processed message number {rocket.last_message_number}. Ignoring.")
                return
            
            if msg_number > rocket.last_message_number + 1:
                print(f"[{channel_id}] Message number {msg_number} is greater than last processed message number {rocket.last_message_number + 1}. Buffering.")
                rocket.message_buffer.append((msg_number, message))
                return
            
            # If we reach this point, it means the message is in order, it can be processed
            
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

            # Process buffered messages
            while rocket.message_buffer:
                buffered_msg_number, buffered_message = rocket.message_buffer[0]
                if buffered_msg_number == rocket.last_message_number + 1:
                    rocket.message_buffer.pop(0)
                    self.process_incoming_message(buffered_message)
                else:
                    break

    def list_rockets_in_fleet(self) -> list[dict]:
        """
        Returns a list of all rockets in the fleet as dictionaries, ordered by launch time.
        
        Returns:
            list[dict]: A list of rocket dictionaries that can be JSON serialized
        """
        with self.lock:
        
            sorted_rockets = sorted(
                self.rockets_fleet.values(),
                key=lambda rocket: rocket.launch_time
            )
            return [rocket.to_dict() for rocket in sorted_rockets]
    
    def list_missions(self) -> list[str]:
        """
        Returns a list of all unique missions across all rockets.
        
        Returns:
            list[str]: A list of unique mission names, sorted alphabetically
        """
        with self.lock:
            missions = {rocket.mission for rocket in self.rockets_fleet.values()}
            return sorted(list(missions))
    
    def get_rockets_by_mission(self, mission: str) -> list[dict]:
        """
        Returns a list of rockets assigned to a specific mission.
        
        Args:
            mission (str): The mission name to filter by
        
        Returns:
            list[dict]: A list of rocket dictionaries assigned to the mission, ordered by launch time
        """
        with self.lock:
            mission_rockets = [
                rocket for rocket in self.rockets_fleet.values() 
                if rocket.mission.lower() == mission.lower()
            ]
            sorted_rockets = sorted(mission_rockets, key=lambda rocket: rocket.launch_time)
            return [rocket.to_dict() for rocket in sorted_rockets]
    
    def get_rocket_by_id(self, rocket_id: str) -> dict | None:
        """
        Returns the details of a specific rocket by its ID.
        
        Args:
            rocket_id (str): The ID of the rocket to retrieve.
        
        Returns:
            dict | None: The rocket details as a dictionary, or None if not found.
        """
        with self.lock:
            rocket = self.rockets_fleet.get(rocket_id)
            return rocket.to_dict() if rocket else None