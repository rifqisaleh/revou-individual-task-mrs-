from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.product_services import (
    create_product, get_all_products, get_product_by_id,
    update_product, delete_product
)

product_bp = Blueprint("products", __name__)

@product_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    product = create_product(request.get_json())
    return jsonify({"msg": "Product created", "id": product.id}), 201

@product_bp.route("/", methods=["GET"])
def list_products():
    filters = request.args
    products = get_all_products(filters)
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "stock": p.stock,
        "seller_id": p.seller_id
    } for p in products])


@product_bp.route("/<int:product_id>", methods=["GET"])
def detail(product_id):
    p = get_product_by_id(product_id)
    return jsonify({
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "stock": p.stock,
        "seller_id": p.seller_id
    })

@product_bp.route("/<int:product_id>", methods=["PUT"])
@jwt_required()
def update(product_id):
    updated = update_product(product_id, request.get_json())
    return jsonify({"msg": "Product updated", "id": updated.id})

@product_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete(product_id):
    delete_product(product_id)
    return jsonify({"msg": "Product deleted"})
