from locust import HttpUser, task, between
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - direct service URLs (no gateway)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")
RAFFLE_SERVICE_URL = os.getenv("RAFFLE_SERVICE_URL", "http://raffle-service:8003")

class RaffleUser(HttpUser):
    """Simulates a user entering raffle during a sneaker drop."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login before starting raffle entries."""
        # Create unique test user credentials
        self.user_id = None
        self.token = None
        self.shoe_sizes = ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
        
        # Attempt to login or register
        self._authenticate()
    
    def _authenticate(self):
        """Register or login a test user."""
        import uuid
        import random
        import httpx
        
        unique_id = str(uuid.uuid4())[:8]
        email = f"testuser_{unique_id}@test.com"
        username = f"testuser_{unique_id}"
        password = "TestPass123"
        
        # Try to register (direct to auth service)
        try:
            register_response = httpx.post(
                f"{AUTH_SERVICE_URL}/register",
                json={
                    "email": email,
                    "username": username,
                    "password": password
                },
                timeout=10
            )
            
            if register_response.status_code == 200:
                logger.info(f"User registered: {email}")
            else:
                logger.debug(f"Registration returned {register_response.status_code}")
        except Exception as e:
            logger.error(f"Registration error: {e}")
        
        # Login (direct to auth service)
        try:
            login_response = httpx.post(
                f"{AUTH_SERVICE_URL}/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                logger.info(f"User authenticated: {self.user_id}")
            else:
                logger.error(f"Login failed: {login_response.status_code}")
        except Exception as e:
            logger.error(f"Login error: {e}")
    
    @task(1)
    def enter_raffle(self):
        """Enter raffle with random shoe size (direct to raffle service)."""
        import random
        import httpx
        
        if not self.token:
            logger.warning("Not authenticated, skipping raffle entry")
            return
        
        shoe_size = random.choice(self.shoe_sizes)
        
        try:
            response = httpx.post(
                f"{RAFFLE_SERVICE_URL}/enter-raffle",
                json={"shoe_size": shoe_size},
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code in [200, 202]:
                logger.debug(f"Raffle entry accepted for size {shoe_size}")
            else:
                logger.warning(f"Raffle entry failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Raffle entry error: {e}")
    
    @task(1)
    def get_products(self):
        """Fetch product list (direct to product service)."""
        import httpx
        
        try:
            response = httpx.get(
                f"{PRODUCT_SERVICE_URL}/products?limit=10",
                timeout=10
            )
            if response.status_code == 200:
                logger.debug("Products fetched successfully")
            else:
                logger.warning(f"Get products failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Get products error: {e}")


class WebsiteUser(HttpUser):
    """Simulates a regular website visitor (lighter load)."""
    
    wait_time = between(5, 10)
    
    @task(2)
    def view_products(self):
        """View products page (direct to product service)."""
        import httpx
        try:
            httpx.get(f"{PRODUCT_SERVICE_URL}/products?limit=20", timeout=10)
        except Exception as e:
            logger.error(f"View products error: {e}")
    
    @task(1)
    def view_raffle_stats(self):
        """Check raffle stats (direct to raffle service)."""
        import httpx
        try:
            httpx.get(f"{RAFFLE_SERVICE_URL}/raffle-stats", timeout=10)
        except Exception as e:
            logger.error(f"View raffle stats error: {e}")
