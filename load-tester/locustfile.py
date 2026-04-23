"""
Locust Load Tester for SneakerDrop Raffle Service
==================================================
Simulates 5,000 concurrent users authenticating and sending
POST requests to the Raffle Ingress Service.

Usage:
    locust -f locustfile.py --host http://raffle-service:8003
    # Then open http://localhost:8089 to configure and start the test.

Environment Variables:
    AUTH_SERVICE_URL — URL of the auth service (default: http://auth-service:8001)
"""

import os
import random

from locust import HttpUser, task, between, events

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

SHOE_SIZES = ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "13"]


class RaffleUser(HttpUser):
    """
    Simulates a user who:
      1. Registers (or logs in if already registered).
      2. Sends repeated POST /enter-raffle requests.
    """

    wait_time = between(0.1, 0.5)  # Aggressive timing for stress test
    token = None

    def on_start(self):
        """Authenticate the user on start."""
        user_id = random.randint(1, 999_999_999)
        username = f"loaduser_{user_id}"
        password = "TestPassword123!"
        email = f"{username}@loadtest.local"

        # Try to register
        import requests

        try:
            resp = requests.post(
                f"{AUTH_SERVICE_URL}/api/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                },
                timeout=10,
            )
        except Exception:
            pass

        # Login to get JWT
        try:
            resp = requests.post(
                f"{AUTH_SERVICE_URL}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10,
            )
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
        except Exception:
            pass

    @task
    def enter_raffle(self):
        """Send a POST to /enter-raffle with a random shoe size."""
        if not self.token:
            return

        size = random.choice(SHOE_SIZES)
        self.client.post(
            "/api/raffle/enter-raffle",
            json={"shoe_size": size},
            headers={"Authorization": f"Bearer {self.token}"},
        )
