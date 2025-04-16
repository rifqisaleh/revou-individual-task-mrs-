from app import db
from app.models.models import CartItem, Product
from flask import abort
from flask_jwt_extended import get_jwt_identity

def add_to_cart(data):
    user_id = int(get_jwt_identity())
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    product = db.session.get(Product, product_id)
    if not product:
        abort(404, "Product not found")

    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return item

def get_cart_items():
    user_id = int(get_jwt_identity())
    return CartItem.query.filter_by(user_id=user_id).all()

def remove_from_cart(item_id):
    user_id = int(get_jwt_identity())
    item = db.session.get(CartItem, item_id)


    if not item or item.user_id != user_id:
        abort(404, "Cart item not found or access denied")

    db.session.delete(item)
    db.session.commit()
    return True

def update_cart_quantity(item_id, quantity):
    user_id = int(get_jwt_identity())
    item = db.session.get(CartItem, item_id)

    if not item or item.user_id != user_id:
        abort(404, "Cart item not found or access denied")

    item.quantity = quantity
    db.session.commit()
    return item

def clear_user_cart():
    user_id = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
