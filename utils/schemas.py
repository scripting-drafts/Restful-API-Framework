AUTH_TOKEN_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "token": {"type": "string", "minLength": 1}
    },
    "required": ["token"],
    "additionalProperties": True
}

BOOKING_OBJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": ["number", "integer"]},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "properties": {
                "checkin": {"type": "string"},
                "checkout": {"type": "string"}
            },
            "required": ["checkin", "checkout"],
            "additionalProperties": True
        },
        "additionalneeds": {"type": "string"}
    },
    "required": [
        "firstname",
        "lastname",
        "totalprice",
        "depositpaid",
        "bookingdates"
    ],
    "additionalProperties": True
}

BOOKING_CREATE_RESPONSE_SCHEMA = {
    "anyOf": [
        {
            "type": "object",
            "properties": {
                "bookingid": {"type": ["number", "integer"]}
            },
            "required": ["bookingid"],
            "additionalProperties": True
        },
        {
            "type": "object",
            "properties": {
                "bookingid": {"type": ["number", "integer"]},
                "booking": BOOKING_OBJECT_SCHEMA
            },
            "required": ["bookingid", "booking"],
            "additionalProperties": True
        }
    ]
}

BOOKINGS_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "bookingid": {"type": ["number", "integer"]}
                },
                "required": ["bookingid"],
                "additionalProperties": True
            },
            {
                "type": "object",
                "properties": {
                    "id": {"type": ["number", "integer"]}
                },
                "required": ["id"],
                "additionalProperties": True
            }
        ]
    }
}
