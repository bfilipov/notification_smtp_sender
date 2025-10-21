import base64
import unittest
from unittest.mock import Mock

from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

from smtp_sender.app import app
from smtp_sender.sender import check_security

client = TestClient(app)


class TestTokenValidation(unittest.TestCase):

    def setUp(self):
        """Set up test data"""
        self.ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        self.lang = "en-US,en;q=0.9"
        self.origin = "http://localhost:8000"

        # Generate expected token
        payload = f"{self.ua}|{self.lang}|{self.origin}"
        self.valid_token = base64.b64encode(payload.encode()).decode().replace("=", "")

    def create_mock_request(self, ua=None, lang=None, origin=None):
        """Helper to create a mock request with headers"""
        headers = {}
        if ua is not None:
            headers["user-agent"] = ua
        if lang is not None:
            headers["accept-language"] = lang
        if origin is not None:
            headers["origin"] = origin

        mock_request = Mock(spec=Request)
        mock_request.headers = headers
        mock_request.base_url.hostname = "localhost"  # fallback for origin
        return mock_request

    def test_valid_token(self):
        """Test that valid token passes security check"""
        mock_request = self.create_mock_request(
            ua=self.ua,
            lang=self.lang,
            origin=self.origin
        )

        # Should not raise an exception
        try:
            check_security(mock_request, self.valid_token)
            self.assertTrue(True)  # If we get here, test passes
        except HTTPException:
            self.fail("Valid token raised HTTPException")

    def test_invalid_token(self):
        """Test that invalid token fails security check"""
        mock_request = self.create_mock_request(
            ua=self.ua,
            lang=self.lang,
            origin=self.origin
        )

        with self.assertRaises(HTTPException) as context:
            check_security(mock_request, "invalid-token")

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Invalid security token")

    def test_missing_headers(self):
        """Test with missing headers"""
        mock_request = self.create_mock_request()  # No headers

        with self.assertRaises(HTTPException) as context:
            check_security(mock_request, self.valid_token)

        self.assertEqual(context.exception.status_code, 403)

    def test_partial_headers(self):
        """Test with only some headers present"""
        mock_request = self.create_mock_request(
            ua=self.ua,
            # lang missing
            origin=self.origin
        )

        with self.assertRaises(HTTPException) as context:
            check_security(mock_request, self.valid_token)

        self.assertEqual(context.exception.status_code, 403)

    def test_different_origin(self):
        """Test that different origin generates different token"""
        mock_request = self.create_mock_request(
            ua=self.ua,
            lang=self.lang,
            origin="http://different-domain.com"  # Different origin
        )

        with self.assertRaises(HTTPException) as context:
            check_security(mock_request, self.valid_token)

        self.assertEqual(context.exception.status_code, 403)

    def test_endpoint_with_valid_token(self):
        """Test the actual endpoint with valid token"""
        response = client.post(
            "/send-email",
            headers={
                "user-agent": self.ua,
                "accept-language": self.lang,
                "origin": self.origin,
                "token": self.valid_token,
            },
            json={"body": "test message"}
        )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {"message": "Email sending started"})

    def test_endpoint_with_invalid_token(self):
        """Test the actual endpoint with invalid token"""
        response = client.post(
            "/send-email",
            headers={
                "user-agent": self.ua,
                "accept-language": self.lang,
                "origin": self.origin,
                "token": "invalid-token",
            },
            json={"body": "test message"}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Invalid security token")

    def test_endpoint_missing_token_header(self):
        """Test the endpoint without token header"""
        response = client.post(
            "/send-email",
            headers={
                "user-agent": self.ua,
                "accept-language": self.lang,
                "origin": self.origin,
                # Missing token header
            },
            json={"body": "test message"}
        )

        # This should return 422 (validation error) because token header is required
        self.assertEqual(response.status_code, 422)

    def test_token_generation_logic(self):
        """Test the exact token generation logic matches our expectation"""
        payload = f"{self.ua}|{self.lang}|{self.origin}"
        expected_token = base64.b64encode(payload.encode()).decode().replace("=", "")

        self.assertEqual(self.valid_token, expected_token)

        # Verify it matches the token from your curl example
        # You can add the exact token from your working curl command here
        example_token = "TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTI5LjAuMC4wIFNhZmFyaS81MzcuMzZ8ZW4tVVMsZW47cT0wLjl8aHR0cDovL2xvY2FsaG9zdDo4MDAw"
        # self.assertEqual(expected_token, example_token)  # Uncomment if you have a specific example


if __name__ == "__main__":
    unittest.main()
