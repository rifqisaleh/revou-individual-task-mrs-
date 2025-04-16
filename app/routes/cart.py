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
