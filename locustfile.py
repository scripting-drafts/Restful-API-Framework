import os
import uuid
from locust import HttpUser, task, between

class RestfulBookerUser(HttpUser):
    wait_time = between(0.5, 2)
    host = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")
    token = None

    def on_start(self):
        # Authenticate once at start to obtain token for authorized operations
        r = self.client.post("/auth", json={"username": "admin", "password": "password123"})
        try:
            self.token = r.json().get("token")
        except Exception:
            self.token = None

    @task(1)
    def ping(self):
        self.client.get("/ping")

    @task(2)
    def auth(self):
        r = self.client.post("/auth", json={"username": "admin", "password": "password123"})
        try:
            self.token = r.json().get("token")
        except Exception:
            self.token = None

    @task(3)
    def create_get_delete_booking(self):
        payload = {
            "firstname": f"Fn-{uuid.uuid4().hex[:8]}",
            "lastname": f"Ln-{uuid.uuid4().hex[:8]}",
            "totalprice": 123,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2026-02-01",
                "checkout": "2026-02-03",
            },
            "additionalneeds": "Breakfast",
        }
        r = self.client.post("/booking", json=payload, headers={"Content-Type": "application/json"})
        if r.status_code in (200, 201):
            try:
                bid = r.json()["bookingid"]
            except Exception:
                return
            self.client.get(f"/booking/{bid}")
            headers = {}
            if self.token:
                headers = {"Cookie": f"token={self.token}"}
            self.client.delete(f"/booking/{bid}", headers=headers)
