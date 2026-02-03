import pytest
from api.endpoints import (
    ping,
    create_token,
    create_booking,
    get_booking,
    delete_booking,
    get_bookings,
)
from utils.payloads import booking_payload

SUCCESS_STATUS = {200, 201, 204}


@pytest.fixture(scope="session")
def admin_token():
    resp = create_token("admin", "password123")
    assert resp.status_code in SUCCESS_STATUS
    body = resp.json()
    assert "token" in body
    return body["token"]


def test_benchmark_ping(benchmark):
    def fn():
        r = ping()
        assert r.status_code in SUCCESS_STATUS
        return r.status_code

    benchmark.pedantic(fn, rounds=10, iterations=1)


def test_benchmark_auth(benchmark):
    def fn():
        r = create_token("admin", "password123")
        assert r.status_code in SUCCESS_STATUS
        return r.json().get("token")

    benchmark.pedantic(fn, rounds=5, iterations=1)


def test_benchmark_bookings_list(benchmark):
    def fn():
        r = get_bookings()
        assert r.status_code == 200
        return len(r.json()) if isinstance(r.json(), list) else 0

    benchmark.pedantic(fn, rounds=5, iterations=1)


def test_benchmark_create_get_delete_flow(benchmark, admin_token):
    def fn():
        create_resp = create_booking(booking_payload())
        assert create_resp.status_code in SUCCESS_STATUS
        create_body = create_resp.json()
        bid = create_body["bookingid"]
        get_resp = get_booking(bid)
        assert get_resp.status_code == 200
        del_resp = delete_booking(bid, admin_token)
        assert del_resp.status_code in SUCCESS_STATUS
        return bid

    benchmark.pedantic(fn, rounds=3, iterations=1)
