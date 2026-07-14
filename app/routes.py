"""API routes for inventory management."""
from flask import Blueprint, request, jsonify
from .models import db, Item

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/health", methods=["GET"])
def health():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "healthy", "service": "technova-inventory"})


@api.route("/items", methods=["GET"])
def get_items():
    """Get all inventory items."""
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])


@api.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Get single item by ID."""
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@api.route("/items", methods=["POST"])
def create_item():
    """Create new inventory item."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Field 'name' is required"}), 400

    if data.get("quantity") is not None and data["quantity"] < 0:
        return jsonify({"error": "Quantity cannot be negative"}), 400

    item = Item(
        name=data["name"],
        description=data.get("description", ""),
        quantity=data.get("quantity", 0),
        price=data.get("price", 0.0),
        category=data.get("category", "Umum"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@api.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """Update existing inventory item."""
    item = Item.query.get_or_404(item_id)
    data = request.get_json()

    if data.get("quantity") is not None and data["quantity"] < 0:
        return jsonify({"error": "Quantity cannot be negative"}), 400

    item.name = data.get("name", item.name)
    item.description = data.get("description", item.description)
    item.quantity = data.get("quantity", item.quantity)
    item.price = data.get("price", item.price)
    item.category = data.get("category", item.category)
    db.session.commit()
    return jsonify(item.to_dict())


@api.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete inventory item."""
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item '{item.name}' deleted"}), 200
