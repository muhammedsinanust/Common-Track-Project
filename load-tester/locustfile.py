"""
Locust Load Tester — SneakerDrop Raffle Service
================================================
Simulates up to 5,000 concurrent users. Each user:
  1. Registers a unique account via the Auth Service (using httpx, not Locust client).
  2. Logs in and stores a JWT.
  3. Hammers POST /api/raffle/enter-raffle with random shoe sizes.

Run via Docker Compose:
    docker compose --profile loadtest up -d load-tester
Then open: http://<EC2_IP>:8089
"""

import os
import random
import httpx

from locust import HttpUser, task, between

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

SHOE_SIZES = ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "13"]


class RaffleUser(HttpUser):
    """
    Simulates a user who registers, logs in, then repeatedly enters the raffle.
    """

    wait_time = between(0.05, 0.3)  # Aggressive — stress-test mode
    token: str | None = None

    def on_start(self):
        """Register + login using a unique random identity."""
        uid = random.randint(1, 999_999_999)
        username = f"loaduser_{uid}"
        password = "TestPassword123!"
        email = f"{username}@loadtest.local"

        # Use httpx for out-of-band auth calls (doesn't count in Locust stats)
        with httpx.Client(timeout=10) as client:
            # Register (may return 409 if user already exists — that's fine)
            client.post(
                f"{AUTH_SERVICE_URL}/api/auth/register",
                json={"username": username, "email": email, "password": password},
            )

            # Login
            resp = client.post(
                f"{AUTH_SERVICE_URL}/api/auth/login",
                json={"username": username, "password": password},
            )
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")

    @task
    def enter_raffle(self):
        """POST /api/raffle/enter-raffle with a random shoe size."""
        if not self.token:
            return

        size = random.choice(SHOE_SIZES)
        self.client.post(
            "/api/raffle/enter-raffle",
            json={"shoe_size": size},
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/raffle/enter-raffle",
        )
