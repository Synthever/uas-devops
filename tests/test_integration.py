"""Integration tests — full CRUD lifecycle."""
import pytest


class TestInventoryCRUDLifecycle:
    """End-to-end CRUD workflow test."""

    def test_full_lifecycle(self, client, db):
        # 1. CREATE
        resp = client.post("/api/items", json={
            "name": "Proyektor Epson",
            "description": "Proyektor ruang rapat",
            "quantity": 5,
            "price": 12000000,
            "category": "Elektronik",
        })
        assert resp.status_code == 201
        item = resp.get_json()
        item_id = item["id"]
        assert item["name"] == "Proyektor Epson"

        # 2. READ
        resp = client.get(f"/api/items/{item_id}")
        assert resp.status_code == 200
        assert resp.get_json()["description"] == "Proyektor ruang rapat"

        # 3. UPDATE
        resp = client.put(f"/api/items/{item_id}", json={
            "quantity": 4,
            "description": "Proyektor ruang rapat (1 dipinjam)"
        })
        assert resp.status_code == 200
        updated = resp.get_json()
        assert updated["quantity"] == 4

        # 4. LIST — should have exactly 1 item
        resp = client.get("/api/items")
        assert len(resp.get_json()) == 1

        # 5. DELETE
        resp = client.delete(f"/api/items/{item_id}")
        assert resp.status_code == 200

        # 6. Verify empty
        resp = client.get("/api/items")
        assert resp.get_json() == []


class TestMultipleItems:
    """Test with multiple items and filtering."""

    def test_create_multiple_and_list(self, client, db):
        items_data = [
            {"name": "Meja Kerja", "quantity": 20, "category": "Furniture"},
            {"name": "Kursi Kantor", "quantity": 20, "category": "Furniture"},
            {"name": "Laptop Dell", "quantity": 10, "category": "Elektronik"},
        ]
        for data in items_data:
            resp = client.post("/api/items", json=data)
            assert resp.status_code == 201

        resp = client.get("/api/items")
        assert len(resp.get_json()) == 3

    def test_delete_one_keeps_others(self, client, db):
        r1 = client.post("/api/items", json={"name": "Item A", "quantity": 1})
        r2 = client.post("/api/items", json={"name": "Item B", "quantity": 2})

        client.delete(f"/api/items/{r1.get_json()['id']}")

        resp = client.get("/api/items")
        remaining = resp.get_json()
        assert len(remaining) == 1
        assert remaining[0]["name"] == "Item B"
