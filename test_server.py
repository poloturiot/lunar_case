import unittest
import json
from server import app, control_center
from control_center import ControlCenter

class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        """Set up test client before each test."""
        self.app = app.test_client()
        self.test_time = "2025-05-14T10:00:00"
        control_center.rockets_fleet.clear()
        
    def test_post_message_valid(self):
        """Test POST /messages with valid launch message."""
        message = {
            "metadata": {
                "channel": "rocket_123",
                "messageNumber": 1,
                "messageType": "RocketLaunched",
                "messageTime": self.test_time
            },
            "message": {
                "launchSpeed": 1000,
                "type": "Falcon",
                "mission": "MoonLanding"
            }
        }
        
        response = self.app.post(
            '/messages',
            data=json.dumps(message),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_post_message_invalid_json(self):
        """Test POST /messages with invalid JSON."""
        response = self.app.post(
            '/messages',
            data='Not json',
            content_type='text/plain'
        )
        
        self.assertEqual(response.status_code, 400)
        
    def test_get_rockets(self):
        """Test GET /rockets endpoint."""
        # First launch a rocket
        self.test_post_message_valid()
        
        response = self.app.get('/rockets')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        
    def test_get_specific_rocket(self):
        """Test GET /rockets/<rocket_id> endpoint."""
        # First launch a rocket
        self.test_post_message_valid()
        
        response = self.app.get('/rockets/rocket_123')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 'rocket_123')
        
    def test_get_nonexistent_rocket(self):
        """Test GET /rockets/<rocket_id> with invalid ID."""
        response = self.app.get('/rockets/nonexistent')
        self.assertEqual(response.status_code, 404)
        
    def test_get_missions(self):
        """Test GET /missions endpoint."""
        # First launch a rocket
        self.test_post_message_valid()
        
        response = self.app.get('/missions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(isinstance(data['missions'], list))
        
    def test_get_rockets_by_mission(self):
        """Test GET /missions/<mission> endpoint."""
        # First launch a rocket
        self.test_post_message_valid()
        
        response = self.app.get('/missions/MoonLanding')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mission'], 'MoonLanding')
        self.assertTrue(isinstance(data['rockets'], list))
        
    def test_get_nonexistent_mission(self):
        """Test GET /missions/<mission> with invalid mission."""
        response = self.app.get('/missions/NonexistentMission')
        self.assertEqual(response.status_code, 404)

    def test_invalid_endpoint(self):
        """Test invalid endpoint."""
        response = self.app.get('/invalid_endpoint')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()