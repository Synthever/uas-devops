"""Unit tests for TechNova Inventory API."""
import json
import pytest


class TestHealthEndpoint:
    """Tests for /api/health."""

    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_body(self, client):
        data = client.get("/api/health").get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "technova-inventory"


class TestCreateItem:
    """Tests for POST /api/items."""

    def test_create_item_success(self, client, db):
        resp = client.post("/api/items", json={
            "name": "Laptop Lenovo",
            "quantity": 10,
            "price": 8500000,
            "category": "Elektronik"
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Laptop Lenovo"
        assert data["quantity"] == 10

    def test_create_item_missing_name(self, client, db):
        resp = client.post("/api/items", json={"quantity": 5})
        assert resp.status_code == 400
        assert "required" in resp.get_json()["error"].lower()

    def test_create_item_negative_quantity(self, client, db):
        resp = client.post("/api/items", json={
            "name": "Mouse", "quantity": -1
        })
        assert resp.status_code == 400
        assert "negative" in resp.get_json()["error"].lower()

    def test_create_item_defaults(self, client, db):
        resp = client.post("/api/items", json={"name": "Pulpen"})
        data = resp.get_json()
        assert data["quantity"] == 0
        assert data["price"] == 0.0
        assert data["category"] == "Umum"


class TestGetItems:
    """Tests for GET /api/items."""

    def test_get_empty_list(self, client, db):
        resp = client.get("/api/items")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_get_items_after_create(self, client, db):
        client.post("/api/items", json={"name": "Keyboard", "quantity": 5})
        client.post("/api/items", json={"name": "Monitor", "quantity": 3})
        resp = client.get("/api/items")
        data = resp.get_json()
        assert len(data) == 2

    def test_get_single_item(self, client, db):
        create_resp = client.post("/api/items", json={
            "name": "SSD 512GB", "quantity": 20
        })
        item_id = create_resp.get_json()["id"]
        resp = client.get(f"/api/items/{item_id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "SSD 512GB"

    def test_get_nonexistent_item(self, client, db):
        resp = client.get("/api/items/9999")
        assert resp.status_code == 404


class TestUpdateItem:
    """Tests for PUT /api/items/<id>."""

    def test_update_item(self, client, db):
        create_resp = client.post("/api/items", json={
            "name": "RAM 8GB", "quantity": 50, "price": 450000
        })
        item_id = create_resp.get_json()["id"]
        resp = client.put(f"/api/items/{item_id}", json={
            "quantity": 45, "price": 420000
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["quantity"] == 45
        assert data["price"] == 420000

    def test_update_negative_quantity(self, client, db):
        create_resp = client.post("/api/items", json={
            "name": "Kabel HDMI", "quantity": 10
        })
        item_id = create_resp.get_json()["id"]
        resp = client.put(f"/api/items/{item_id}", json={"quantity": -5})
        assert resp.status_code == 400


class TestDeleteItem:
    """Tests for DELETE /api/items/<id>."""

    def test_delete_item(self, client, db):
        create_resp = client.post("/api/items", json={
            "name": "Charger", "quantity": 8
        })
        item_id = create_resp.get_json()["id"]
        resp = client.delete(f"/api/items/{item_id}")
        assert resp.status_code == 200
        # Verify deleted
        get_resp = client.get(f"/api/items/{item_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_item(self, client, db):
        resp = client.delete("/api/items/9999")
        assert resp.status_code == 404
