import unittest
from datetime import datetime
from control_center import ControlCenter

class TestControlCenter(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.control_center = ControlCenter()
        self.test_time = "2025-05-14T10:00:00"
        self.channel_id = "rocket_123"

    def test_process_launch_message(self):
        """Test processing a rocket launch message."""
        launch_message = {
            "metadata": {
                "channel": self.channel_id,
                "messageNumber": 1,
                "messageType": "RocketLaunched",
                "messageTime": self.test_time
            },
            "message": {
                "launchSpeed": 1000,
                "type": "Falcon",
                "mission": "Moon Landing"
            }
        }

        self.control_center.process_incoming_message(launch_message)
        
        # Verify rocket was added to fleet
        rocket = self.control_center.rockets_fleet.get(self.channel_id)
        self.assertIsNotNone(rocket)
        self.assertEqual(rocket.speed, 1000)
        self.assertEqual(rocket.mission, "Moon Landing")
        self.assertEqual(rocket.last_message_number, 1)

    def test_process_speed_increase(self):
        """Test processing a speed increase message."""
        # First launch the rocket
        self.test_process_launch_message()

        speed_message = {
            "metadata": {
                "channel": self.channel_id,
                "messageNumber": 2,
                "messageType": "RocketSpeedIncreased",
                "messageTime": self.test_time
            },
            "message": {
                "by": 500
            }
        }

        self.control_center.process_incoming_message(speed_message)
        rocket = self.control_center.rockets_fleet.get(self.channel_id)
        self.assertEqual(rocket.speed, 1500)
        self.assertEqual(rocket.last_message_number, 2)

    def test_out_of_order_messages(self):
        """Test handling of out-of-order messages."""
        # First launch the rocket
        self.test_process_launch_message()

        # Send message 3 before message 2
        speed_message_3 = {
            "metadata": {
                "channel": self.channel_id,
                "messageNumber": 3,
                "messageType": "RocketSpeedIncreased",
                "messageTime": self.test_time
            },
            "message": {
                "by": 500
            }
        }

        self.control_center.process_incoming_message(speed_message_3)
        rocket = self.control_center.rockets_fleet.get(self.channel_id)
        self.assertEqual(len(rocket.message_buffer), 1)
        self.assertEqual(rocket.last_message_number, 1)  # Still at launch message

        # Send message 2
        speed_message_2 = {
            "metadata": {
                "channel": self.channel_id,
                "messageNumber": 2,
                "messageType": "RocketSpeedIncreased",
                "messageTime": self.test_time
            },
            "message": {
                "by": 100
            }
        }
        self.control_center.process_incoming_message(speed_message_2)
        self.assertEqual(len(rocket.message_buffer), 0)  # Buffer should be empty
        self.assertEqual(rocket.last_message_number, 3)  # Message 2 and 3 processed 
        self.assertEqual(rocket.speed, 1600)  # Speed should be updated

    def test_ignore_duplicates(self):
        """Test handling duplicate messages."""
        # First launch the rocket
        self.test_process_launch_message()

        # Send duplicate message
        duplicate_message = {
            "metadata": {
                "channel": self.channel_id,
                "messageNumber": 2,
                "messageType": "RocketSpeedIncreased",
                "messageTime": self.test_time
            },
            "message": {
                "by": 500
            }
        }

        rocket = self.control_center.rockets_fleet.get(self.channel_id)

        # Process the message a first time
        self.control_center.process_incoming_message(duplicate_message)
        self.assertEqual(rocket.speed, 1500)  # Speed has increased

        # Process the same message a second time
        self.control_center.process_incoming_message(duplicate_message)
        self.assertEqual(rocket.speed, 1500)  # Speed has not changed

    def test_no_duplicates_in_buffer(self):
        """Test handling of duplicate messages in buffer."""
        # First launch the rocket
        self.test_process_launch_message()

        # Out of order message (will go to the buffer)
        duplicate_message = {
            "metadata": {
                "channel": self.channel_id,
                "messageNumber": 5,
                "messageType": "RocketSpeedIncreased",
                "messageTime": self.test_time
            },
            "message": {
                "by": 500
            }
        }

        rocket = self.control_center.rockets_fleet.get(self.channel_id)

        # Try to process the message a first time
        self.control_center.process_incoming_message(duplicate_message)
        self.assertEqual(len(rocket.message_buffer), 1) # Buffer should have the message

        # Process the same message a second time
        self.control_center.process_incoming_message(duplicate_message)
        self.assertEqual(len(rocket.message_buffer), 1) # Message as not been added again
        

    def test_invalid_message_structure(self):
        """Test handling of invalid message structure."""
        invalid_message = {
            "metadata": {
                "channel": self.channel_id,
                # Missing required fields
            },
            "message": {}
        }

        # Should not raise exception but log error
        self.control_center.process_incoming_message(invalid_message)
        self.assertEqual(len(self.control_center.rockets_fleet), 0)

    def test_message_for_nonexistent_rocket(self):
        """Test handling message for rocket that hasn't launched."""
        speed_message = {
            "metadata": {
                "channel": "nonexistent_rocket",
                "messageNumber": 1,
                "messageType": "RocketSpeedIncreased",
                "messageTime": self.test_time
            },
            "message": {
                "by": 500
            }
        }

        self.control_center.process_incoming_message(speed_message)
        self.assertNotIn("nonexistent_rocket", self.control_center.rockets_fleet)

    def test_handle_speed_increase(self):
        """Test handling of speed increase message."""
        # First launch the rocket
        self.test_process_launch_message()
        rocket = self.control_center.rockets_fleet.get(self.channel_id)
        initial_speed = rocket.speed

        # Test speed increase
        self.control_center._handle_speed_increase(
            rocket=rocket,
            payload={"by": 500},
            msg_time_str=self.test_time,
            msg_number=2
        )

        self.assertEqual(rocket.speed, initial_speed + 500)
        self.assertEqual(rocket.last_message_number, 2)
        self.assertEqual(rocket.last_update_time, datetime.fromisoformat(self.test_time))

    def test_handle_speed_decrease(self):
        """Test handling of speed decrease message."""
        # First launch the rocket
        self.test_process_launch_message()
        rocket = self.control_center.rockets_fleet.get(self.channel_id)
        initial_speed = rocket.speed

        # Test speed decrease
        self.control_center._handle_speed_decrease(
            rocket=rocket,
            payload={"by": 300},
            msg_time_str=self.test_time,
            msg_number=2
        )

        self.assertEqual(rocket.speed, initial_speed - 300)
        self.assertEqual(rocket.last_message_number, 2)
        self.assertEqual(rocket.last_update_time, datetime.fromisoformat(self.test_time))

    def test_handle_explosion(self):
        """Test handling of explosion message."""
        # First launch the rocket
        self.test_process_launch_message()
        rocket = self.control_center.rockets_fleet.get(self.channel_id)

        # Test explosion
        explosion_reason = "Fuel tank rupture"
        self.control_center._handle_explosion(
            rocket=rocket,
            payload={"reason": explosion_reason},
            msg_time_str=self.test_time,
            msg_number=2
        )

        self.assertEqual(rocket.status, "Exploded")
        self.assertEqual(rocket.explosion_reason, explosion_reason)
        self.assertEqual(rocket.last_message_number, 2)
        self.assertEqual(rocket.last_update_time, datetime.fromisoformat(self.test_time))

    def test_handle_mission_change(self):
        """Test handling of mission change message."""
        # First launch the rocket
        self.test_process_launch_message()
        rocket = self.control_center.rockets_fleet.get(self.channel_id)
        initial_mission = rocket.mission

        # Test mission change
        new_mission = "Mars Landing"
        self.control_center._handle_mission_change(
            rocket=rocket,
            payload={"newMission": new_mission},
            msg_time_str=self.test_time,
            msg_number=2
        )

        self.assertNotEqual(rocket.mission, initial_mission)
        self.assertEqual(rocket.mission, new_mission)
        self.assertEqual(rocket.last_message_number, 2)
        self.assertEqual(rocket.last_update_time, datetime.fromisoformat(self.test_time))

if __name__ == '__main__':
    unittest.main()