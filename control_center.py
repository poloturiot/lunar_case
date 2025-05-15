from datetime import datetime
import logging
import threading
from rocket import Rocket
class ControlCenter:
    def __init__(self):
        self.rockets_fleet: dict[str, Rocket] = {}
        # Reentrant lock. RLock allows a thread to acquire the lock multiple times. Useful in recursive functions
        self.fleet_lock = threading.Lock()

    def process_incoming_message(self, message: any):
        """Processes incoming messages from the API server."""
        if not self._validate_message(message):
            return

        metadata, payload = message.get("metadata", {}), message.get("message", {})

        channel_id = metadata.get("channel")
        msg_number = metadata.get("messageNumber")
        msg_type = metadata.get("messageType")
        msg_time_str = metadata.get("messageTime")

        with self.fleet_lock:
            rocket = self._get_or_create_rocket(channel_id, msg_type, metadata, payload)
            if not rocket:
                return

        with rocket.lock:
            if self._should_ignore_message(rocket, msg_number):
                return

            if msg_number > rocket.last_message_number + 1:
                self._buffer_message(rocket, msg_number, message)
                return

            self._process_message(rocket, msg_type, payload, msg_time_str, msg_number)
            self._process_buffered_messages(rocket)

    def _validate_message(self, message: dict) -> bool:
        """Validates message structure and required fields."""
        metadata = message.get("metadata", {})
        return all([
            metadata.get("channel"),
            isinstance(metadata.get("messageNumber"), int),
            metadata.get("messageType"),
            metadata.get("messageTime")
        ])

    def _get_or_create_rocket(self, channel_id: str, msg_type: str, 
                            metadata: dict, payload: dict) -> Rocket | None:
        """Gets existing rocket or creates new one if it's a launch message."""
        rocket = self.rockets_fleet.get(channel_id)
        if not rocket and msg_type == "RocketLaunched":
            rocket = self._create_new_rocket(channel_id, metadata, payload)
            self.rockets_fleet[channel_id] = rocket
            logging.info(f"Rocket {channel_id} added to fleet.")
        return rocket

    def _create_new_rocket(self, channel_id: str, metadata: dict, payload: dict) -> Rocket:
        """Creates a new rocket instance."""
        return Rocket(
            id=channel_id,
            launch_time=metadata.get("messageTime"),
            last_update_time=metadata.get("messageTime"),
            last_message_number=metadata.get("messageNumber"),
            speed=payload.get("launchSpeed"),
            rocket_type=payload.get("type"),
            mission=payload.get("mission")
        )

    def _should_ignore_message(self, rocket: Rocket, msg_number: int) -> bool:
        """Determines if message should be ignored based on message number."""
        if msg_number <= rocket.last_message_number:
            logging.warning(f"[{rocket.id}] Message {msg_number} is too old. Ignoring.")
            return True
        return False

    def _buffer_message(self, rocket: Rocket, msg_number: int, message: dict):
        """Buffers out-of-order message if not already buffered."""
        for buffered_msg_number, _ in rocket.message_buffer:
            if buffered_msg_number == msg_number:
                logging.info(f"[{rocket.id}] Message {msg_number} already buffered. Ignoring.")
                return
        rocket.append_message_to_buffer(msg_number, message)
        logging.info(f"[{rocket.id}] Message {msg_number} added to buffer.")

    def _process_message(self, rocket: Rocket, msg_type: str, 
                        payload: dict, msg_time_str: str, msg_number: int):
        """Processes message based on its type."""
        handlers = {
            "RocketSpeedIncreased": self._handle_speed_increase,
            "RocketSpeedDecreased": self._handle_speed_decrease,
            "RocketExploded": self._handle_explosion,
            "RocketMissionChanged": self._handle_mission_change
        }
        if handler := handlers.get(msg_type):
            handler(rocket, payload, msg_time_str, msg_number)

    def _handle_speed_increase(self, rocket: Rocket, payload: dict, 
                             msg_time_str: str, msg_number: int):
        """Handles speed increase message."""
        speed_increment = payload.get("by")
        rocket.increase_speed(speed_increment, msg_time_str, msg_number)
        logging.info(f"[{rocket.id}] Speed increased by {speed_increment}. New speed: {rocket.speed}.")

    def _handle_speed_decrease(self, rocket: Rocket, payload: dict, 
                             msg_time_str: str, msg_number: int):
        """Handles speed decrease message."""
        speed_decrement = payload.get("by")
        rocket.decrease_speed(speed_decrement, msg_time_str, msg_number)
        logging.info(f"[{rocket.id}] Speed decreased by {speed_decrement}. New speed: {rocket.speed}.")

    def _handle_explosion(self, rocket: Rocket, payload: dict, 
                         msg_time_str: str, msg_number: int):
        """Handles explosion message."""
        reason = payload.get("reason")
        rocket.explode(reason, msg_time_str, msg_number)
        logging.info(f"[{rocket.id}] Rocket exploded. Reason: {reason}.")

    def _handle_mission_change(self, rocket: Rocket, payload: dict, 
                             msg_time_str: str, msg_number: int):
        """Handles mission change message."""
        new_mission = payload.get("newMission")
        rocket.update_mission(new_mission, msg_time_str, msg_number)
        logging.info(f"[{rocket.id}] Mission changed to {new_mission}.")

    def _process_buffered_messages(self, rocket: Rocket):
        """Processes any buffered messages that are now ready."""
        # Check if there is a message in the buffer
        if not rocket.message_buffer:
            return
        
        # A heap is used, so root of the list is the message with the smallest message number
        buffered_msg_number, buffered_message = rocket.message_buffer[0]
        if buffered_msg_number == rocket.last_message_number + 1:
            rocket.pop_message_from_buffer()
            self.process_incoming_message(buffered_message)

    def list_rockets_in_fleet(self) -> list[dict]:
        """
        Returns a list of all rockets in the fleet as dictionaries, ordered by launch time.
        
        Returns:
            list[dict]: A list of rocket dictionaries that can be JSON serialized
        """
        with self.fleet_lock:
        
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
        with self.fleet_lock:
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
        with self.fleet_lock:
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
        with self.fleet_lock:
            rocket = self.rockets_fleet.get(rocket_id)
            return rocket.to_dict() if rocket else None