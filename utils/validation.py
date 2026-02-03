from typing import Any
from jsonschema import Draft7Validator
from .schemas import (
    AUTH_TOKEN_RESPONSE_SCHEMA,
    BOOKING_OBJECT_SCHEMA,
    BOOKING_CREATE_RESPONSE_SCHEMA,
    BOOKINGS_LIST_SCHEMA,
)

SCHEMAS = {
    "auth_token_response": AUTH_TOKEN_RESPONSE_SCHEMA,
    "booking_object": BOOKING_OBJECT_SCHEMA,
    "booking_create_response": BOOKING_CREATE_RESPONSE_SCHEMA,
    "bookings_list": BOOKINGS_LIST_SCHEMA,
}


def validate_schema(data: Any, schema_name: str) -> None:
    schema = SCHEMAS.get(schema_name)
    assert schema is not None, f"Unknown schema: {schema_name}"

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    assert not errors, _format_errors(errors)


def _format_errors(errors) -> str:
    msgs = []
    for err in errors:
        path = "/".join(str(p) for p in err.path) or "<root>"
        msgs.append(f"{path}: {err.message}")
    return "Schema validation failed: " + "; ".join(msgs)
