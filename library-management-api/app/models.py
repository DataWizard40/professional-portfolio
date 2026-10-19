from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        # The database itself refuses impossible copy counts.
        CheckConstraint("available_copies >= 0", name="ck_books_available_not_negative"),
        CheckConstraint(
            "available_copies <= total_copies", name="ck_books_available_not_above_total"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(255), index=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    published_year: Mapped[int | None]
    total_copies: Mapped[int] = mapped_column(default=1)
    available_copies: Mapped[int] = mapped_column(default=1)

    loans: Mapped[list["Loan"]] = relationship(back_populates="book")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    loans: Mapped[list["Loan"]] = relationship(back_populates="member")


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        # Speeds up "which books does this member have right now?"
        Index("ix_loans_member_returned", "member_id", "returned_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    due_date: Mapped[date] = mapped_column(Date)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime)  # NULL = still borrowed

    book: Mapped[Book] = relationship(back_populates="loans")
    member: Mapped[Member] = relationship(back_populates="loans")
