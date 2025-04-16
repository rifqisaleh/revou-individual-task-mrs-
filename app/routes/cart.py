from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.cart_service import add_to_cart, get_cart_items, remove_from_cart

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/", methods=["POST"])
@jwt_required()
def add():
    item = add_to_cart(request.get_json())
    return jsonify({"msg": "Item added to cart", "item_id": item.id}), 201

@cart_bp.route("/", methods=["GET"])
@jwt_required()
def get():
    cart = get_cart_items()
    return jsonify([
        {
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity
        } for item in cart
    ])

@cart_bp.route("/<int:item_id>/", methods=["DELETE"])
@jwt_required()
def delete(item_id):
    remove_from_cart(item_id)
    return jsonify({"msg": "Item removed from cart"})


@cart_bp.route("/<int:item_id>/", methods=["PATCH"])
@jwt_required()
def update_quantity(item_id):
    data = request.get_json()
    new_quantity = data.get("quantity")

    if new_quantity is None or not isinstance(new_quantity, int) or new_quantity < 1:
        return jsonify({"msg": "Invalid quantity"}), 400

    from app.services.cart_service import update_cart_quantity
    item = update_cart_quantity(item_id, new_quantity)
    return jsonify({"msg": "Quantity updated", "item_id": item.id, "new_quantity": item.quantity})


@cart_bp.route("/", methods=["DELETE"])
@jwt_required()
def clear_cart():
    from app.services.cart_service import clear_user_cart
    clear_user_cart()
    return jsonify({"msg": "Cart cleared"}), 200
