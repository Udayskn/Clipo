import unittest
from unittest.mock import patch,Mock
from flask import Flask, jsonify, request
from app import app  # Assuming your Flask application instance is named 'app'

class TestEntryCRUD(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass
    def test_retrieve_entries(self):
        # Make a request to the endpoint
        response = self.app.get('/')

        # Assert response status code
        self.assertEqual(response.status_code, 200)

       
    def test_update_entry_unauthenticated(self):
        # Mock token validation
        with patch('app.token_required') as mock_validate_token:
            mock_validate_token.return_value = False  # Assuming token is invalid or not provided

            # Make a request without a token
            response = self.app.put('/update_entry/1', data={'title': 'New Title', 'description': 'New Description', 'status': 'active'})

            # Assert response status code and message
            self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
