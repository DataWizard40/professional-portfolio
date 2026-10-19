NEW_PRODUCT = {"name": "Mouse", "sku": "MS-1", "price": "15.50", "quantity": 5}


def test_admin_can_create_product(client, admin_headers):
    response = client.post("/products", json=NEW_PRODUCT, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Mouse"


def test_customer_cannot_create_product(client, user_headers):
    response = client.post("/products", json=NEW_PRODUCT, headers=user_headers)
    assert response.status_code == 403


def test_duplicate_sku_rejected(client, admin_headers):
    client.post("/products", json=NEW_PRODUCT, headers=admin_headers)
    response = client.post("/products", json=NEW_PRODUCT, headers=admin_headers)
    assert response.status_code == 400


def test_negative_price_rejected(client, admin_headers):
    bad = {**NEW_PRODUCT, "price": "-1.00"}
    assert client.post("/products", json=bad, headers=admin_headers).status_code == 422


def test_list_search_and_in_stock_filter(client, admin_headers):
    for name, qty in [("Blue Mouse", 3), ("Red Mouse", 0), ("Monitor", 2)]:
        body = {"name": name, "sku": name.upper().replace(" ", "-"), "price": "10", "quantity": qty}
        client.post("/products", json=body, headers=admin_headers)

    names = [p["name"] for p in client.get("/products", params={"search": "mouse"}).json()]
    assert names == ["Blue Mouse", "Red Mouse"]

    names = [p["name"] for p in client.get("/products", params={"in_stock": True}).json()]
    assert names == ["Blue Mouse", "Monitor"]

    page = client.get("/products", params={"skip": 1, "limit": 1}).json()
    assert [p["name"] for p in page] == ["Monitor"]


def test_update_product(client, admin_headers, product):
    response = client.patch(
        f"/products/{product.id}", json={"price": "30.00"}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["price"] == "30.00"
    assert response.json()["quantity"] == 10  # unchanged


def test_delete_product(client, admin_headers, product):
    assert client.delete(f"/products/{product.id}", headers=admin_headers).status_code == 204
    assert client.get(f"/products/{product.id}").status_code == 404


def test_cannot_delete_ordered_product(client, admin_headers, user_headers, product):
    client.post(
        "/orders", json={"items": [{"product_id": product.id, "quantity": 1}]}, headers=user_headers
    )
    response = client.delete(f"/products/{product.id}", headers=admin_headers)
    assert response.status_code == 400


def test_get_missing_product(client):
    assert client.get("/products/999").status_code == 404
