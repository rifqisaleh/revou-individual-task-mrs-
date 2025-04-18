from app import db
from app.models.models import CartItem, Order, OrderItem, Product, Transaction
from datetime import datetime


def checkout(user_id, data=None):
    print("✅ CHECKOUT STARTED for user_id:", user_id)

    # Fetch cart items for the user
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    print("→ CART ITEMS:", cart_items)

    if not cart_items:
        print("🛒 Cart is empty.")
        return None, "Cart is empty"

    total = 0
    order = Order(user_id=user_id, total_amount=0, status="pending", created_at=datetime.utcnow())
    db.session.add(order)
    db.session.commit()  # Commit now to generate order.id

    for item in cart_items:
        product = db.session.get(Product, item.product_id)

        if not product:
            print(f"❌ Product ID {item.product_id} not found.")
            return None, f"Product with ID {item.product_id} not found"

        if product.stock < item.quantity:
            print(f"❌ Not enough stock for product {product.name}")
            return None, f"Not enough stock for product '{product.name}'"

        # Deduct stock
        product.stock -= item.quantity
        total += product.price * item.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price
        )
        db.session.add(order_item)

    # Update total after processing items
    order.total_amount = total

    # Clear the user's cart
    CartItem.query.filter_by(user_id=user_id).delete()

    db.session.commit()

    
    if data is None:
        data = {}

    method = data.get("payment_method", "bank_transfer")

    transaction = Transaction(
        order_id=order.id,
        method=method,
        amount=order.total_amount,
        status="pending"
    )
    db.session.add(transaction)
    db.session.commit()
    

    print("✅ CHECKOUT COMPLETE — Order ID:", order.id)
    return order, None


def get_user_orders(user_id):
    return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()


def get_order_with_items(user_id, order_id):
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return None, "Order not found"
    return order, None

def update_order_status(user_id, order_id, status):
    order = db.session.get(Order, order_id)
    if not order:
        return None, "Order not found"

    order.status = status
    db.session.commit()
    return order, None