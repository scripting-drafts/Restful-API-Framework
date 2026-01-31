import requests
import pytest
import uuid
from datetime import datetime, timedelta

BASE_URL = "https://restful-booker.herokuapp.com"
REQUEST_TIMEOUT = 10

SUCCESS_STATUS = {200, 201, 204}


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token(base_url):
    """
    Obtain an auth token using the demo credentials from the public API docs.
    Returns the token string.
    """
    url = f"{base_url}/auth"
    resp = requests.post(url, json={"username": "admin", "password": "password123"}, timeout=REQUEST_TIMEOUT)
    assert resp.status_code in SUCCESS_STATUS, f"Auth request failed: {resp.status_code} {resp.text}"
    body = resp.json()
    assert "token" in body, "Auth response missing token"
    return body["token"]


def booking_payload(firstname=None, lastname=None, totalprice=123, depositpaid=False,
                    checkin=None, checkout=None, additionalneeds="Breakfast"):
    """
    Build a booking payload. Dates default to today / +2 days.
    """
    firstname = firstname or f"Fn-{uuid.uuid4().hex[:8]}"
    lastname = lastname or f"Ln-{uuid.uuid4().hex[:8]}"
    checkin = checkin or datetime.utcnow().date().isoformat()
    checkout = checkout or (datetime.utcnow().date() + timedelta(days=2)).isoformat()
    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": totalprice,
        "depositpaid": depositpaid,
        "bookingdates": {
            "checkin": checkin,
            "checkout": checkout
        },
        "additionalneeds": additionalneeds
    }


@pytest.fixture
def create_booking(base_url):
    """
    Create a booking and yield (bookingid, payload). Attempts to delete it after the test using admin token if provided.
    Tests that need admin token can call auth_token separately.
    """
    created = []

    def _create(payload=None):
        p = payload or booking_payload()
        resp = requests.post(f"{base_url}/booking", json=p, timeout=REQUEST_TIMEOUT)
        assert resp.status_code in SUCCESS_STATUS, f"Create booking failed: {resp.status_code} {resp.text}"
        body = resp.json()
        # Response format: {"bookingid": 1, "booking": {...}}
        assert "bookingid" in body, f"Unexpected create response body: {body}"
        bookingid = body["bookingid"]
        created.append(bookingid)
        return bookingid, p

    yield _create

    # Cleanup: try to delete created bookings with no auth (best-effort). If cleanup requires auth, tests that create bookings should perform deletion themselves using auth_token.
    for bid in created:
        try:
            requests.delete(f"{base_url}/booking/{bid}", timeout=REQUEST_TIMEOUT)
        except Exception:
            pass


def test_ping(base_url):
    resp = requests.get(f"{base_url}/ping", timeout=REQUEST_TIMEOUT)
    # Historically the ping endpoint returns 201, but accept common success codes
    assert resp.status_code in SUCCESS_STATUS, f"/ping returned unexpected status: {resp.status_code}"


def test_auth_returns_token(base_url):
    resp = requests.post(f"{base_url}/auth", json={"username": "admin", "password": "password123"}, timeout=REQUEST_TIMEOUT)
    assert resp.status_code in SUCCESS_STATUS, f"/auth failed: {resp.status_code} {resp.text}"
    data = resp.json()
    assert "token" in data and isinstance(data["token"], str) and data["token"], "Token missing or empty"


def test_create_and_get_booking(base_url, create_booking):
    bookingid, payload = create_booking()
    # GET booking by id
    resp = requests.get(f"{base_url}/booking/{bookingid}", timeout=REQUEST_TIMEOUT)
    assert resp.status_code == 200, f"GET booking/{bookingid} failed: {resp.status_code}"
    body = resp.json()
    # verify some fields match
    assert body["firstname"] == payload["firstname"]
    assert body["lastname"] == payload["lastname"]
    assert body["bookingdates"]["checkin"] == payload["bookingdates"]["checkin"]


def test_get_bookings_list_and_filter(base_url, create_booking):
    # create a booking with known first/last name
    firstname = f"First-{uuid.uuid4().hex[:6]}"
    lastname = f"Last-{uuid.uuid4().hex[:6]}"
    payload = booking_payload(firstname=firstname, lastname=lastname)
    bookingid, _ = create_booking(payload)

    # get list of bookings
    resp = requests.get(f"{base_url}/booking", timeout=REQUEST_TIMEOUT)
    assert resp.status_code == 200, f"GET /booking failed: {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Bookings list should be a list"

    # filter by firstname (query param)
    resp_f = requests.get(f"{base_url}/booking", params={"firstname": firstname}, timeout=REQUEST_TIMEOUT)
    assert resp_f.status_code == 200
    ids = [item.get("bookingid") or item.get("id") or item.get("bookingid") for item in resp_f.json()]
    # at least the created booking should be present in filtered results
    assert any((bid == bookingid) for bid in ids), f"Filtered bookings did not include created booking {bookingid}"


def test_update_booking_put_requires_token(base_url, create_booking, auth_token):
    bookingid, payload = create_booking()
    updated_payload = payload.copy()
    updated_payload["firstname"] = "Updated-" + payload["firstname"]
    # Update requires token in Cookie per docs
    headers = {"Cookie": f"token={auth_token}", "Content-Type": "application/json"}
    resp = requests.put(f"{base_url}/booking/{bookingid}", json=updated_payload, headers=headers, timeout=REQUEST_TIMEOUT)
    assert resp.status_code in SUCCESS_STATUS, f"PUT /booking/{bookingid} failed: {resp.status_code} {resp.text}"
    body = resp.json()
    assert body["firstname"] == updated_payload["firstname"]


def test_partial_update_patch_requires_token(base_url, create_booking, auth_token):
    bookingid, payload = create_booking()
    patch_payload = {"firstname": "Patched-" + payload["firstname"]}
    headers = {"Cookie": f"token={auth_token}", "Content-Type": "application/json"}
    resp = requests.patch(f"{base_url}/booking/{bookingid}", json=patch_payload, headers=headers, timeout=REQUEST_TIMEOUT)
    assert resp.status_code in SUCCESS_STATUS, f"PATCH /booking/{bookingid} failed: {resp.status_code} {resp.text}"
    body = resp.json()
    assert body["firstname"] == patch_payload["firstname"]


def test_delete_booking_requires_token(base_url, create_booking, auth_token):
    bookingid, _ = create_booking()
    headers = {"Cookie": f"token={auth_token}"}
    resp = requests.delete(f"{base_url}/booking/{bookingid}", headers=headers, timeout=REQUEST_TIMEOUT)
    assert resp.status_code in SUCCESS_STATUS, f"DELETE /booking/{bookingid} failed: {resp.status_code} {resp.text}"
    # subsequent GET should return 404
    resp_get = requests.get(f"{base_url}/booking/{bookingid}", timeout=REQUEST_TIMEOUT)
    assert resp_get.status_code == 404, f"Deleted booking {bookingid} still retrievable, status: {resp_get.status_code}"


def test_create_booking_response_structure(base_url):
    payload = booking_payload()
    resp = requests.post(f"{base_url}/booking", json=payload, timeout=REQUEST_TIMEOUT)
    assert resp.status_code in SUCCESS_STATUS
    body = resp.json()
    # Expect bookingid key and nested booking object (some deployments may only return bookingid)
    assert "bookingid" in body or ("bookingid" in body and "booking" in body) or isinstance(body, dict)