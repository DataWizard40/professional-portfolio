from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Book, Loan, Member
from app.schemas import LoanCreate, LoanOut

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
def borrow_book(loan_in: LoanCreate, db: Session = Depends(get_db)):
    """Lend a book to a member.

    Rules:
    - the book must have a copy available
    - the member can't have more than `max_active_loans` books at once
    - the member can't borrow a second copy of a book they already have
    """
    book = db.get(Book, loan_in.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if db.get(Member, loan_in.member_id) is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if book.available_copies == 0:
        raise HTTPException(status_code=400, detail="No copies of this book are available")

    active_loans = db.scalar(
        select(func.count())
        .select_from(Loan)
        .where(Loan.member_id == loan_in.member_id, Loan.returned_at.is_(None))
    )
    if active_loans >= settings.max_active_loans:
        raise HTTPException(
            status_code=400,
            detail=f"Members can borrow at most {settings.max_active_loans} books at a time",
        )

    already_has_it = db.scalar(
        select(Loan).where(
            Loan.member_id == loan_in.member_id,
            Loan.book_id == loan_in.book_id,
            Loan.returned_at.is_(None),
        )
    )
    if already_has_it:
        raise HTTPException(status_code=400, detail="Member already has this book")

    loan = Loan(
        book_id=book.id,
        member_id=loan_in.member_id,
        due_date=date.today() + timedelta(days=settings.loan_days),
    )
    book.available_copies -= 1
    db.add(loan)
    db.commit()  # the loan and the copy count are saved together
    db.refresh(loan)
    return loan


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.returned_at is not None:
        raise HTTPException(status_code=400, detail="This book has already been returned")

    loan.returned_at = datetime.now()
    loan.book.available_copies += 1
    db.commit()
    db.refresh(loan)
    return loan


@router.get("", response_model=list[LoanOut])
def list_loans(current_only: bool = False, db: Session = Depends(get_db)):
    query = select(Loan)
    if current_only:
        query = query.where(Loan.returned_at.is_(None))
    return db.scalars(query.order_by(Loan.id.desc())).all()
