from app.models import Product
from tests.conftest import auth_header, make_user


def get_quantity(db, product_id):
    # End the test session's current transaction so we see the API's committed changes
    # (MySQL keeps showing the old snapshot until the transaction ends).
    db.rollback()
    return db.get(Product, product_id).quantity


def order_body(product_id, quantity):
    return {"items": [{"product_id": product_id, "quantity": quantity}]}


def test_place_order_reduces_stock(client, db, user_headers, product):
    response = client.post("/orders", json=order_body(product.id, 3), headers=user_headers)
    assert response.status_code == 201
    assert response.json()["total"] == "75.00"
    assert response.json()["status"] == "placed"
    assert get_quantity(db, product.id) == 7


def test_not_enough_stock(client, db, user_headers, product):
    response = client.post("/orders", json=order_body(product.id, 11), headers=user_headers)
    assert response.status_code == 400
    assert get_quantity(db, product.id) == 10


def test_failed_order_saves_nothing(client, db, user_headers, product):
    """If one item fails, stock for the other items must not change either."""
    items = {
        "items": [{"product_id": product.id, "quantity": 2}, {"product_id": 999, "quantity": 1}]
    }
    response = client.post("/orders", json=items, headers=user_headers)
    assert response.status_code == 404
    assert get_quantity(db, product.id) == 10


def test_cancel_order_restocks(client, db, user_headers, product):
    order = client.post("/orders", json=order_body(product.id, 4), headers=user_headers).json()

    response = client.post(f"/orders/{order['id']}/cancel", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert get_quantity(db, product.id) == 10

    # Cancelling twice is not allowed (and must not restock twice).
    assert client.post(f"/orders/{order['id']}/cancel", headers=user_headers).status_code == 400
    assert get_quantity(db, product.id) == 10


def test_users_only_see_their_own_orders(client, db, product):
    alice = auth_header(make_user(db, "alice@example.com"))
    bob = auth_header(make_user(db, "bob@example.com"))
    order = client.post("/orders", json=order_body(product.id, 1), headers=alice).json()

    assert client.get(f"/orders/{order['id']}", headers=bob).status_code == 404
    assert len(client.get("/orders", headers=alice).json()) == 1
    assert client.get("/orders", headers=bob).json() == []


def test_order_keeps_original_price(client, admin_headers, user_headers, product):
    order = client.post("/orders", json=order_body(product.id, 1), headers=user_headers).json()
    client.patch(f"/products/{product.id}", json={"price": "99.00"}, headers=admin_headers)

    saved = client.get(f"/orders/{order['id']}", headers=user_headers).json()
    assert saved["items"][0]["unit_price"] == "25.00"
