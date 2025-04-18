import json  # Add this import for JSON serialization
from flask_jwt_extended import create_access_token
from app.models.models import User, Product, CartItem, db, Transaction

def setup_user_cart(test_app):
    with test_app.app_context():
        user = User(
            username="tester",
            email="tester@mail.com",
            password="hashedpass",
            full_name="Test User",
            role="user"
        )
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Test Item",
            description="A good product",
            price=10.0,
            stock=5,
            image_url="http://example.com/image.jpg",
            seller_id=user.id
        )
        db.session.add(product)
        db.session.commit()

        cart = CartItem(user_id=user.id, product_id=product.id, quantity=2)
        db.session.add(cart)
        db.session.commit()

        token = create_access_token(identity=str(user.id), fresh=True)
        headers = {"Authorization": f"Bearer {token}"}
        return user, product, headers


def test_successful_checkout(client, test_app):
    user, product, headers = setup_user_cart(test_app)
    res = client.post("/orders/checkout", json={}, headers=headers)
    print("✔️ RES:", res.status_code, res.get_json())
    assert res.status_code == 201


def test_empty_cart_checkout(client, test_app):
    with test_app.app_context():
        user = User(
            username="noitems",
            email="noitems@mail.com",
            password="hashedpass",
            full_name="Empty User",
            role="user"
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=str(user.id))
        headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/orders/checkout", json={}, headers=headers)
    print("✔️ RES:", res.status_code, res.get_json())
    assert res.status_code == 400


def test_get_user_orders(client, test_app):
    user, product, headers = setup_user_cart(test_app)
    client.post("/orders/checkout", json={}, headers=headers)

    res = client.get("/orders/me", headers=headers)
    data = res.get_json()
    print("📦 USER ORDERS:", res.status_code, data)

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "items" in data[0]


def test_get_single_order(client, test_app):
    user, product, headers = setup_user_cart(test_app)
    checkout_res = client.post("/orders/checkout", json={}, headers=headers)
    order_id = checkout_res.get_json().get("order_id")

    res = client.get(f"/orders/{order_id}", headers=headers)
    data = res.get_json()
    print("📦 SINGLE ORDER:", res.status_code, data)

    assert res.status_code == 200
    assert data["id"] == order_id
    assert "items" in data
    assert isinstance(data["items"], list)


def test_patch_order_status(client, test_app):
    with test_app.app_context():
        # Create admin
        admin = User(username="adminuser", email="admin@mail.com", password="hashed", full_name="Admin", role="admin")
        db.session.add(admin)

        # Create regular user
        buyer = User(username="buyer", email="buyer@mail.com", password="hashed", full_name="Buyer", role="user")
        db.session.add(buyer)
        db.session.commit()

        # Create product
        product = Product(
            name="Patch Item",
            description="x",
            price=15.0,
            stock=10,
            image_url="x",
            seller_id=admin.id
        )
        db.session.add(product)
        db.session.commit()

        # Add item to buyer's cart
        cart_item = CartItem(user_id=buyer.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()

        # Checkout using buyer token with role info
        buyer_token = create_access_token(identity=str(buyer.id), additional_claims={"role": buyer.role})
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

        res = client.post("/orders/checkout", json={}, headers=buyer_headers)
        print("🚨 CHECKOUT RESPONSE:", res.status_code, res.get_json())

        # Validate response and handle missing order_id
        response_data = res.get_json()
        assert res.status_code == 201, f"Unexpected status code: {res.status_code}, Response: {response_data}"
        assert "order_id" in response_data, f"Missing 'order_id' in response: {response_data}"
        order_id = response_data["order_id"]

        # Patch order status using admin token with role info
        admin_token = create_access_token(identity=str(admin.id), additional_claims={"role": admin.role})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        patch_res = client.patch(f"/orders/{order_id}", json={"status": "shipped"}, headers=admin_headers)

        assert patch_res.status_code == 200
        assert patch_res.get_json()["msg"] == "Order updated successfully"


def test_transactions_created_on_checkout(client, test_app):
    user, product, headers = setup_user_cart(test_app)
    # Query product price in a fresh session to avoid DetachedInstanceError
    with test_app.app_context():
        product_db = Product.query.filter_by(name="Test Item").first()
        product_price = product_db.price

    res = client.post("/orders/checkout", json={"payment_method": "credit_card"}, headers=headers)
    data = res.get_json()
    print("Checkout Result:", res.status_code, data)

    assert res.status_code == 201
    order_id = data.get("order_id")
    assert order_id is not None

    with test_app.app_context():
        tx = Transaction.query.filter_by(order_id=order_id).first()
        assert tx is not None
        assert tx.method == "credit_card"
        assert tx.status == "pending"
        assert tx.amount == product_price * 2  # use captured price
