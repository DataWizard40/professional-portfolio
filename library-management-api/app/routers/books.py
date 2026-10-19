from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Loan
from app.schemas import BookCreate, BookOut, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])


def get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("", response_model=list[BookOut])
def list_books(
    search: str | None = Query(None, description="Search by title or author"),
    available_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Book)
    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Book.title.ilike(pattern), Book.author.ilike(pattern)))
    if available_only:
        query = query.where(Book.available_copies > 0)
    query = query.order_by(Book.title).offset(skip).limit(limit)
    return db.scalars(query).all()


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return get_book_or_404(db, book_id)


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def add_book(book_in: BookCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Book).where(Book.isbn == book_in.isbn)):
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists")

    # All copies are on the shelf when a book is first added.
    book = Book(**book_in.model_dump(), available_copies=book_in.total_copies)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.patch("/{book_id}", response_model=BookOut)
def update_book(book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)):
    book = get_book_or_404(db, book_id)
    changes = book_in.model_dump(exclude_unset=True)

    if "total_copies" in changes:
        on_loan = book.total_copies - book.available_copies
        if changes["total_copies"] < on_loan:
            raise HTTPException(
                status_code=400,
                detail=f"{on_loan} copies are on loan, so total_copies can't be lower than that",
            )
        book.available_copies = changes["total_copies"] - on_loan

    for field, value in changes.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = get_book_or_404(db, book_id)
    # Keep loan history intact: books that were ever borrowed can't be deleted.
    if db.scalar(select(Loan).where(Loan.book_id == book_id).limit(1)):
        raise HTTPException(
            status_code=400, detail="This book has loan history and can't be deleted"
        )
    db.delete(book)
    db.commit()
