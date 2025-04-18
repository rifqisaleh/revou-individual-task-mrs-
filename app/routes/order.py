from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.order_service import checkout, get_user_orders, get_order_with_items, update_order_status
from app.core.authorization import role_required

order_bp = Blueprint("orders", __name__)

@order_bp.route("/checkout", methods=["POST"])
@jwt_required()
def create_order():
    print("🛬 /orders/checkout was reached")
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    print("✅ JWT received, user_id =", user_id)
    print("Received Payment Method:", data.get("payment_method"))

    order, error = checkout(user_id, data)
    if error:
        print("❌ Checkout error:", error)
        return jsonify({"msg": error}), 400

    print("✅ Order created: ID =", order.id)
    return jsonify({"msg": "Checkout successful", "order_id": order.id}), 201


@order_bp.route("/me", methods=["GET"])
@jwt_required()
def get_user_order_list():
    user_id = get_jwt_identity()
    orders = get_user_orders(user_id)

    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price
                } for item in order.order_items
            ]
        })

    return jsonify(result), 200


@order_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order_detail(order_id):
    user_id = get_jwt_identity()
    order, error = get_order_with_items(user_id, order_id)

    if error:
        return jsonify({"msg": error}), 404

    return jsonify({
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price
            } for item in order.order_items
        ]
    }), 200


@order_bp.route("/<int:order_id>", methods=["PATCH"])
@jwt_required()
@role_required("admin", "seller")  
def patch_order_status(order_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"msg": "Missing 'status' in request"}), 400

    order, error = update_order_status(user_id, order_id, new_status)
    if error:
        return jsonify({"msg": error}), 404

    return jsonify({
        "msg": "Order updated successfully",
        "order_id": order.id,
        "new_status": order.status
    }), 200
