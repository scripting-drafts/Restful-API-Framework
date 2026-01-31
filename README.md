# Restful API Framework

A small Python test suite and framework for exercising the Restful-Booker API (https://restful-booker.herokuapp.com).  
This repository contains integration-style pytest tests that exercise the main endpoints (ping, auth, create/list/get/update/patch/delete bookings). Tests are intended to run against the public demo service but can be adapted to use mocks for offline testing or CI.

> Note: The repository language is Python and the test suite uses `pytest` and `requests`.

## Quick start

1. Clone the repository and change into the project root:
   ```bash
   git clone <repo-url>
   cd restful_api_framework
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS / Linux
   .venv\Scripts\Activate.ps1     # Windows PowerShell
   pip install -r requirements.txt
   ```
   If `requirements.txt` is not present, install the minimal deps:
   ```bash
   pip install pytest requests
   ```

3. Run the full test suite (integration tests hit the live demo API):
   ```bash
   pytest -q
   ```

## Environment / Configuration

- BASE_URL
  - Default (used in tests): `https://restful-booker.herokuapp.com`
  - You can override this to point tests at another server:
    ```bash
    export BASE_URL="http://localhost:3000"   # macOS / Linux
    setx BASE_URL "http://localhost:3000"     # Windows (new session required)
    ```

- AUTH_USERNAME / AUTH_PASSWORD
  - Default used by tests: `admin` / `password123`
  - You can override if your server uses different credentials:
    ```bash
    export AUTH_USERNAME="admin"
    export AUTH_PASSWORD="password123"
    ```

## Test design

- Tests are written with `pytest`.
- They exercise the public API directly and therefore are integration tests that require network access.
- Fixtures include:
  - `base_url` — base endpoint
  - `auth_token` — obtains an auth token from `/auth` and is used for update/delete operations
  - `create_booking` — helper fixture to create bookings and perform best-effort cleanup
- Recommended marker:
  - Mark integration tests with `@pytest.mark.integration` if you want to skip them during fast/local runs:
    ```bash
    pytest -m "not integration"
    pytest -m integration
    ```

## Running a single test

Run a single test file:
```bash
pytest tests/test_restful_booker.py::test_create_and_get_booking -q
```

Run tests matching a keyword:
```bash
pytest -k create -q
```

## Offline / Mocked testing

If you prefer not to hit the live service:
- Use libraries such as `responses`, `requests-mock`, or `vcrpy` to stub HTTP interactions.
- Example (install):
  ```bash
  pip install responses
  ```
- Replace network calls in tests with mocked responses, or add a pytest fixture that toggles a `requests` adapter.

If you want, we can provide a mocked test example or switch the suite to use recorded responses (vcrpy).

## Project layout (convention)

- api/                 - optional in-repo application code (if applicable)
- tests/               - pytest test modules (integration tests go here)
  - conftest.py        - shared fixtures and sys.path adjustments (if needed)
- requirements.txt     - Python dependencies
- README.md

## Continuous integration

- Add a CI step to create a virtualenv, install `-r requirements.txt`, and run `pytest`.
- For public demo tests, consider isolating or gating integration tests so CI does not fail due to external service outages. Use `pytest -m "not integration"` in fast CI pipelines, and run integration tests separately.

Example GitHub Actions (concept)
```yaml
name: Python tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: "3.10"
      - run: python -m venv .venv && . .venv/bin/activate
      - run: pip install -r requirements.txt
      - run: pytest -q -m "not integration"
```

## Contributing

- Open an issue or submit a PR with improvements.
- Prefer small, focused PRs (fixes, additional tests, mock conversions).
- Add tests for new behavior and make sure they pass locally before submitting.

## Troubleshooting

- Network failures: the demo server may be rate-limited or down. Retry later or run with mocked responses.
- Authentication/permission errors: ensure correct credentials via environment variables.
