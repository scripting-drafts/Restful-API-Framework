import os
import time
import uuid
import json
import threading
import statistics
import requests

BASE_URL = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")
USERS = int(os.getenv("USERS", "5"))
DURATION = int(os.getenv("DURATION", "15"))


def worker(stats):
    session = requests.Session()
    end = time.time() + DURATION
    token = None
    while time.time() < end:
        t0 = time.perf_counter()
        r = session.get(f"{BASE_URL}/ping")
        stats["ping"].append((time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        r = session.post(f"{BASE_URL}/auth", json={"username": "admin", "password": "password123"})
        try:
            token = r.json().get("token")
        except Exception:
            token = None
        stats["auth"].append((time.perf_counter() - t0) * 1000)

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
        t0 = time.perf_counter()
        cr = session.post(f"{BASE_URL}/booking", json=payload, headers={"Content-Type": "application/json"})
        stats["create"].append((time.perf_counter() - t0) * 1000)
        bid = None
        try:
            bid = cr.json().get("bookingid")
        except Exception:
            bid = None
        if bid:
            t0 = time.perf_counter()
            session.get(f"{BASE_URL}/booking/{bid}")
            stats["get"].append((time.perf_counter() - t0) * 1000)
            cookies = {"token": token} if token else None
            t0 = time.perf_counter()
            session.delete(f"{BASE_URL}/booking/{bid}", cookies=cookies or {})
            stats["delete"].append((time.perf_counter() - t0) * 1000)


def summarize(stats):
    def m(d):
        if not d:
            return {}
        return {
            "count": len(d),
            "mean_ms": round(statistics.mean(d), 2),
            "p95_ms": round(statistics.quantiles(d, n=100)[94], 2) if len(d) >= 100 else None,
        }

    out = {k: m(v) for k, v in stats.items()}
    print(json.dumps(out, indent=2))


def main():
    stats = {"ping": [], "auth": [], "create": [], "get": [], "delete": []}
    threads = [threading.Thread(target=worker, args=(stats,), daemon=True) for _ in range(USERS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    summarize(stats)


if __name__ == "__main__":
    main()
