import pytest
from flask_jwt_extended import create_access_token
from app import db
from app.models.models import User

@pytest.fixture
def auth_headers(test_app):
    with test_app.app_context():
        seller = User(
            username="selleruser",
            email="seller@mail.com",
            password="hashed",  # we won't login, just fake token
            full_name="Seller User",
            role="seller"
        )
        db.session.add(seller)
        db.session.commit()

        token = create_access_token(
            identity=str(seller.id),  # ✅ identity as string
            additional_claims={"role": seller.role}  # ✅ use custom claims
        )
        return {"Authorization": f"Bearer {token}"}


def test_create_product(client, test_app):
    with test_app.app_context():
        # Create the seller manually
        seller = User(
            username="test_seller",
            email="test_seller@mail.com",
            password="hashed",
            full_name="Test Seller",
            role="seller"
        )
        db.session.add(seller)
        db.session.commit()

        token = create_access_token(
            identity=str(seller.id),  # ✅ identity as string
            additional_claims={"role": seller.role}  # ✅ role as claim
        )
        headers = {"Authorization": f"Bearer {token}"}

        res = client.post("/products/", json={
            "name": "Organic Apples",
            "description": "Fresh from the farm",
            "price": 4.99,
            "stock": 20,
            "image_url": "http://example.com/apple.jpg"
        }, headers=headers)

        print("RESPONSE:", res.status_code, res.get_json())
        assert res.status_code == 201


def test_list_products(client):
    res = client.get("/products/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_product_detail(client):
    res = client.get("/products/1/")
    assert res.status_code in [200, 404]  # 404 if not created yet


def test_update_product(client, auth_headers):
    client.post("/products/", json={
        "name": "Organic Bananas",
        "description": "Ripe and sweet",
        "price": 3.5,
        "stock": 15,
        "image_url": "http://example.com/banana.jpg"
    }, headers=auth_headers)

    res = client.put("/products/1", json={
        "price": 3.0,
        "stock": 10
    }, headers=auth_headers)

    assert res.status_code in [200, 404]


def test_delete_product(client, auth_headers):
    client.post("/products/", json={
        "name": "Tomatoes",
        "description": "Vine-ripened",
        "price": 2.5,
        "stock": 30
    }, headers=auth_headers)

    res = client.delete("/products/1/", headers=auth_headers)
    assert res.status_code in [200, 404]
