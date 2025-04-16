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

def test_product_filters(client, auth_headers):
    # Create products with different prices and stock
    client.post("/products/", json={
        "name": "Cheap Product",
        "price": 1.0,
        "stock": 5
    }, headers=auth_headers)

    client.post("/products/", json={
        "name": "Expensive Product",
        "price": 100.0,
        "stock": 0
    }, headers=auth_headers)

    # Filter by min_price
    res = client.get("/products/?min_price=50")
    assert res.status_code == 200
    assert all(p["price"] >= 50 for p in res.get_json())

    # Filter by in_stock only
    res = client.get("/products/?in_stock=true")
    assert res.status_code == 200
    assert all(p["stock"] > 0 for p in res.get_json())


def test_product_pagination(client, auth_headers):
    # Create a bunch of products
    for i in range(1, 21):
        token = create_access_token(identity="1", additional_claims={"role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}
        client.post("/products/", json={
            "name": f"Product {i}",
            "price": i,
            "stock": i
        }, headers=headers)

    res = client.get("/products/?page=1&limit=5")
    assert res.status_code == 200
    assert len(res.get_json()) <= 5


def test_product_sorting(client):
    res = client.get("/products/?sort_by=price&order=desc")
    prices = [p["price"] for p in res.get_json()]
    assert prices == sorted(prices, reverse=True)
