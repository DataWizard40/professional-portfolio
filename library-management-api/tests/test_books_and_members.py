from tests.conftest import add_book, add_member, borrow


def test_add_and_get_book(client):
    book = add_book(client, copies=3)
    assert book["total_copies"] == 3
    assert book["available_copies"] == 3
    assert client.get(f"/books/{book['id']}").json()["title"] == "Clean Code"


def test_duplicate_isbn_rejected(client):
    book = add_book(client)
    body = {"title": "Copy", "author": "Someone", "isbn": book["isbn"]}
    assert client.post("/books", json=body).status_code == 400


def test_invalid_isbn_rejected(client):
    body = {"title": "Bad", "author": "Someone", "isbn": "12-34"}
    assert client.post("/books", json=body).status_code == 422


def test_search_and_available_filter(client):
    add_book(client, title="Learning SQL", author="Alan Beaulieu")
    add_book(client, title="Python Crash Course", author="Eric Matthes")
    sql_book = add_book(client, title="SQL Antipatterns", author="Bill Karwin")
    borrow(client, sql_book, add_member(client))

    titles = [b["title"] for b in client.get("/books", params={"search": "sql"}).json()]
    assert titles == ["Learning SQL", "SQL Antipatterns"]

    titles = [b["title"] for b in client.get("/books", params={"search": "matthes"}).json()]
    assert titles == ["Python Crash Course"]

    available = client.get("/books", params={"available_only": True}).json()
    assert "SQL Antipatterns" not in [b["title"] for b in available]


def test_changing_total_copies_keeps_loans_in_mind(client):
    book = add_book(client, copies=3)
    borrow(client, book, add_member(client, "Ada Lovelace"))
    borrow(client, book, add_member(client, "Alan Turing"))

    # 2 copies are on loan, so the total can't drop to 1.
    assert client.patch(f"/books/{book['id']}", json={"total_copies": 1}).status_code == 400

    updated = client.patch(f"/books/{book['id']}", json={"total_copies": 5}).json()
    assert updated["total_copies"] == 5
    assert updated["available_copies"] == 3


def test_delete_book(client):
    book = add_book(client)
    assert client.delete(f"/books/{book['id']}").status_code == 204
    assert client.get(f"/books/{book['id']}").status_code == 404


def test_cannot_delete_book_with_loan_history(client):
    book = add_book(client)
    borrow(client, book, add_member(client))
    assert client.delete(f"/books/{book['id']}").status_code == 400


def test_add_member_and_duplicate_email(client):
    member = add_member(client, email="ada@example.com")
    assert member["name"] == "Ada Lovelace"
    body = {"name": "Someone Else", "email": "ADA@example.com"}
    assert client.post("/members", json=body).status_code == 400


def test_missing_records_return_404(client):
    assert client.get("/books/999").status_code == 404
    assert client.get("/members/999").status_code == 404
    assert client.get("/members/999/loans").status_code == 404
