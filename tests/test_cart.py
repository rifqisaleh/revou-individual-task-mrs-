from flask_jwt_extended import create_access_token
from app import db
from app.models.models import User, Product

def get_auth_header_for_user(app, username="cartuser"):
    with app.app_context():
        # Create user
        user = User(
            username=username,
            email=f"{username}@mail.com",
            password="hashed",
            full_name="Cart User",
            role="user"
        )
        db.session.add(user)
        db.session.commit()

        # Create product
        product = Product(
            name="Test Product",
            description="For cart testing",
            price=9.99,
            stock=100,
            seller_id=1  # Change to user.id if needed
        )
        db.session.add(product)
        db.session.commit()

        # Generate JWT
        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )
        headers = {"Authorization": f"Bearer {token}"}

        return user.id, product.id, headers  # ✅ Only return IDs and headers


def test_add_to_cart(client, test_app):
    _, product_id, headers = get_auth_header_for_user(test_app)

    res = client.post("/cart/", json={
        "product_id": product_id,
        "quantity": 3
    }, headers=headers)

    assert res.status_code == 201
    assert "item_id" in res.get_json()


def test_get_cart(client, test_app):
    _, product_id, headers = get_auth_header_for_user(test_app)

    # Add item
    client.post("/cart/", json={
        "product_id": product_id,
        "quantity": 2
    }, headers=headers)

    res = client.get("/cart/", headers=headers)

    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
    assert res.get_json()[0]["product_id"] == product_id


def test_remove_from_cart(client, test_app):
    _, product_id, headers = get_auth_header_for_user(test_app)

    # Add item
    res_add = client.post("/cart/", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers)

    item_id = res_add.get_json()["item_id"]

    # Remove item
    res = client.delete(f"/cart/{item_id}/", headers=headers)

    assert res.status_code == 200
    assert res.get_json()["msg"] == "Item removed from cart"
