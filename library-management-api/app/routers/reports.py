"""Reports built with SQL joins and aggregation (GROUP BY / COUNT).

The same queries written as plain SQL are in sql/example_queries.sql.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Loan, Member
from app.schemas import OverdueLoan, PopularBook

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/overdue", response_model=list[OverdueLoan])
def overdue_loans(db: Session = Depends(get_db)):
    """Books that haven't been returned and are past their due date."""
    today = date.today()
    query = (
        select(Loan.id, Book.title, Member.name, Member.email, Loan.due_date)
        .join(Book, Loan.book_id == Book.id)
        .join(Member, Loan.member_id == Member.id)
        .where(Loan.returned_at.is_(None), Loan.due_date < today)
        .order_by(Loan.due_date)
    )
    return [
        OverdueLoan(
            loan_id=loan_id,
            book_title=title,
            member_name=name,
            member_email=email,
            due_date=due_date,
            days_overdue=(today - due_date).days,
        )
        for loan_id, title, name, email, due_date in db.execute(query)
    ]


@router.get("/popular-books", response_model=list[PopularBook])
def popular_books(limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    """The most borrowed books of all time."""
    times_borrowed = func.count(Loan.id).label("times_borrowed")
    query = (
        select(Book.id, Book.title, Book.author, times_borrowed)
        .join(Loan, Loan.book_id == Book.id)
        .group_by(Book.id, Book.title, Book.author)
        .order_by(times_borrowed.desc(), Book.title)
        .limit(limit)
    )
    return [
        PopularBook(book_id=book_id, title=title, author=author, times_borrowed=count)
        for book_id, title, author, count in db.execute(query)
    ]
