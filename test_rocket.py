import unittest
from datetime import datetime
from rocket import Rocket

class TestRocket(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_rocket = Rocket(
            id="rocket_123",
            launch_time="2025-05-14T10:00:00",
            last_update_time="2025-05-14T10:01:00",
            last_message_number=1,
            speed=1000,
            rocket_type="Falcon",
            mission="Moon Landing"
        )

    def test_rocket_initialization(self):
        """Test rocket initialization with valid parameters."""
        self.assertEqual(self.test_rocket.id, "rocket_123")
        self.assertEqual(self.test_rocket.launch_time, datetime.fromisoformat("2025-05-14T10:00:00"))
        self.assertEqual(self.test_rocket.speed, 1000)
        self.assertEqual(self.test_rocket.status, "Launched")
        self.assertIsNone(self.test_rocket.explosion_reason)

    def test_increase_speed(self):
        """Test speed increase functionality."""
        initial_speed = self.test_rocket.speed
        increment = 500
        self.test_rocket.increase_speed(increment)
        self.assertEqual(self.test_rocket.speed, initial_speed + increment)

    def test_decrease_speed(self):
        """Test speed decrease functionality."""
        initial_speed = self.test_rocket.speed
        decrement = 500
        self.test_rocket.decrease_speed(decrement)
        self.assertEqual(self.test_rocket.speed, initial_speed - decrement)

    def test_explosion(self):
        """Test rocket explosion functionality."""
        reason = "Fuel tank rupture"
        self.test_rocket.explod(reason)
        self.assertEqual(self.test_rocket.status, "Exploded")
        self.assertEqual(self.test_rocket.explosion_reason, reason)

    def test_update_mission(self):
        """Test mission update functionality."""
        new_mission = "Mars Landing"
        self.test_rocket.update_mission(new_mission)
        self.assertEqual(self.test_rocket.mission, new_mission)

    def test_to_dict(self):
        """Test dictionary serialization."""
        rocket_dict = self.test_rocket.to_dict()
        self.assertEqual(rocket_dict["id"], "rocket_123")
        self.assertEqual(rocket_dict["speed"], 1000)
        self.assertEqual(rocket_dict["status"], "Launched")
        self.assertEqual(rocket_dict["mission"], "Moon Landing")

if __name__ == '__main__':
    unittest.main()