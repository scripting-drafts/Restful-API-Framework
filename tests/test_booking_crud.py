import pytest
from api.endpoints import (
    create_booking, get_booking, get_bookings,
    create_token, update_booking, delete_booking
)
from utils.payloads import booking_payload, updated_booking_payload
from utils.validation import validate_schema

@pytest.fixture(scope="module")
def token():
    return create_token("admin", "password123").json()["token"]

def test_booking_crud_flow(token):
    create = create_booking(booking_payload())
    create_body = create.json()
    validate_schema(create_body, "booking_create_response")
    booking_id = create_body["bookingid"]

    get_resp = get_booking(booking_id)
    assert get_resp.status_code == 200
    validate_schema(get_resp.json(), "booking_object")

    update = update_booking(booking_id, updated_booking_payload(), token)
    assert update.status_code == 200
    validate_schema(update.json(), "booking_object")

    delete = delete_booking(booking_id, token)
    assert delete.status_code in (200, 201)
