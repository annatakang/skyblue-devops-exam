import json
import sys
import time
import urllib.request
import uuid

base = sys.argv[1].rstrip("/")
environment = sys.argv[2]

def request(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    payload = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(
        base + path, data=payload, headers=headers, method=method
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.status, json.load(response)

for attempt in range(12):
    try:
        status, login = request(
            "POST", "/api/login",
            {"username": "admin", "password": "a"}
        )
        token = login["access_token"]
        assert token, "Missing access token"
        break
    except Exception:
        if attempt == 11:
            raise
        time.sleep(5)

print("PASS: gateway login")

status, users = request("GET", "/api/users", token=token)
assert status == 200 and isinstance(users, list) and users
print("PASS: authenticated user retrieval")

status, orders = request("GET", "/api/orders", token=token)
assert status == 200 and isinstance(orders, list)
print("PASS: authenticated order retrieval")

if environment != "prod":
    item = "ci-" + uuid.uuid4().hex
    status, created = request(
        "POST", "/api/orders",
        {"address": "SkyBlue CI test, York", "item": item},
        token
    )
    assert status == 200 and created["item"] == item
    status, orders = request("GET", "/api/orders", token=token)
    assert any(
        order["id"] == created["id"] and order["item"] == item
        for order in orders
    ), "Created order missing"
    print("PASS: order creation and retrieval")

print("Integration checks passed for " + environment)
