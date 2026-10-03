"""Integration tests for the /monitors API endpoints."""


def test_list_monitors_empty(client):
    resp = client.get("/monitors/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_monitor(client):
    payload = {"name": "Google", "url": "https://google.com", "interval_minutes": 5}
    resp = client.post("/monitors/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Google"
    assert data["url"] == "https://google.com"
    assert data["current_status"] == "unknown"
    assert data["id"] is not None


def test_create_monitor_invalid_url(client):
    resp = client.post("/monitors/", json={"name": "Bad", "url": "not-a-url"})
    assert resp.status_code == 422


def test_get_monitor(client):
    created = client.post("/monitors/", json={"name": "Example", "url": "https://example.com"}).json()
    resp = client.get(f"/monitors/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_monitor_not_found(client):
    resp = client.get("/monitors/9999")
    assert resp.status_code == 404


def test_update_monitor(client):
    created = client.post("/monitors/", json={"name": "Old", "url": "https://example.com"}).json()
    resp = client.put(f"/monitors/{created['id']}", json={"name": "New", "interval_minutes": 10})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"
    assert resp.json()["interval_minutes"] == 10


def test_delete_monitor(client):
    created = client.post("/monitors/", json={"name": "Del", "url": "https://example.com"}).json()
    resp = client.delete(f"/monitors/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/monitors/{created['id']}").status_code == 404


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
