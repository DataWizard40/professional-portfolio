from datetime import date, timedelta

from app.models import Loan
from tests.conftest import add_book, add_member, borrow


def test_borrow_and_return(client):
    book, member = add_book(client), add_member(client)

    response = borrow(client, book, member)
    assert response.status_code == 201
    loan = response.json()
    assert loan["due_date"] == str(date.today() + timedelta(days=14))
    assert client.get(f"/books/{book['id']}").json()["available_copies"] == 0

    response = client.post(f"/loans/{loan['id']}/return")
    assert response.status_code == 200
    assert response.json()["returned_at"] is not None
    assert client.get(f"/books/{book['id']}").json()["available_copies"] == 1


def test_cannot_return_twice(client):
    loan = borrow(client, add_book(client), add_member(client)).json()
    client.post(f"/loans/{loan['id']}/return")
    assert client.post(f"/loans/{loan['id']}/return").status_code == 400


def test_no_copies_left(client):
    book = add_book(client, copies=1)
    borrow(client, book, add_member(client, "Ada Lovelace"))
    response = borrow(client, book, add_member(client, "Alan Turing"))
    assert response.status_code == 400


def test_loan_limit(client):
    member = add_member(client)
    for i in range(3):
        assert borrow(client, add_book(client, title=f"Book {i}"), member).status_code == 201
    response = borrow(client, add_book(client, title="One too many"), member)
    assert response.status_code == 400


def test_cannot_borrow_same_book_twice(client):
    book, member = add_book(client, copies=2), add_member(client)
    borrow(client, book, member)
    assert borrow(client, book, member).status_code == 400


def test_member_loan_history(client):
    member = add_member(client)
    first = borrow(client, add_book(client, title="First"), member).json()
    borrow(client, add_book(client, title="Second"), member)
    client.post(f"/loans/{first['id']}/return")

    history = client.get(f"/members/{member['id']}/loans").json()
    assert len(history) == 2
    current = client.get(f"/members/{member['id']}/loans", params={"current_only": True}).json()
    assert len(current) == 1


def test_overdue_report(client, db):
    member = add_member(client, "Grace Hopper")
    late = borrow(client, add_book(client, title="Late Book"), member).json()
    borrow(client, add_book(client, title="On Time Book"), member)

    # Pretend the first loan was due 5 days ago.
    loan = db.get(Loan, late["id"])
    loan.due_date = date.today() - timedelta(days=5)
    db.commit()

    report = client.get("/reports/overdue").json()
    assert len(report) == 1
    assert report[0]["book_title"] == "Late Book"
    assert report[0]["member_name"] == "Grace Hopper"
    assert report[0]["days_overdue"] == 5


def test_popular_books_report(client):
    popular = add_book(client, title="Popular", copies=3)
    quiet = add_book(client, title="Quiet")
    add_book(client, title="Never Borrowed")

    for name in ["Ada Lovelace", "Alan Turing", "Grace Hopper"]:
        borrow(client, popular, add_member(client, name))
    borrow(client, quiet, add_member(client, "Linus Torvalds"))

    report = client.get("/reports/popular-books").json()
    assert [(b["title"], b["times_borrowed"]) for b in report] == [("Popular", 3), ("Quiet", 1)]
