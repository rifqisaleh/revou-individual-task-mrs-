import sys
from app import db
from app.models.models import Product
from flask import abort
from flask_jwt_extended import get_jwt_identity, get_jwt


def create_product(data):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    print("CREATE DATA:", data, file=sys.stderr, flush=True)
    print("JWT IDENTITY:", user_id, "ROLE:", claims["role"], file=sys.stderr, flush=True)

    if claims["role"] not in ["admin", "seller"]:
        abort(403, "Only admin or seller can create products")

    try:
        product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            stock=data["stock"],
            image_url=data.get("image_url", ""),
            seller_id=user_id,
        )
    except Exception as e:
        print("CREATE PRODUCT ERROR:", e, file=sys.stderr, flush=True)
        raise

    try:
        db.session.add(product)
        db.session.commit()
    except Exception as e:
        print("DB COMMIT ERROR:", e, file=sys.stderr, flush=True)
        raise

    return product


def get_all_products():
    return Product.query.all()


def get_product_by_id(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        abort(404, "Product not found")
    return product


def update_product(product_id, data):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    product = db.session.get(Product, product_id)


    if not product:
        abort(404, "Product not found")

    if user_id != product.seller_id and claims["role"] != "admin":
        abort(403, "Not authorized to update this product")

    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.price = data.get("price", product.price)
    product.stock = data.get("stock", product.stock)
    product.image_url = data.get("image_url", product.image_url)

    db.session.commit()
    return product


def delete_product(product_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    product = db.session.get(Product, product_id)


    if not product:
        abort(404, "Product not found")

    if user_id != product.seller_id and claims["role"] != "admin":
        abort(403, "Not authorized to delete this product")

    db.session.delete(product)
    db.session.commit()
    return True
