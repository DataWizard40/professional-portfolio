"""Pydantic models that define what the API accepts and returns."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- Books -------------------------------------------------------------------


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str = Field(pattern=r"^\d{10}(\d{3})?$", description="10 or 13 digits")
    published_year: int | None = Field(default=None, ge=1000, le=2100)
    total_copies: int = Field(default=1, ge=1, le=100)


class BookUpdate(BaseModel):
    """All fields optional, so only the fields sent are changed."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    published_year: int | None = Field(default=None, ge=1000, le=2100)
    total_copies: int | None = Field(default=None, ge=1, le=100)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: str
    published_year: int | None
    total_copies: int
    available_copies: int


# --- Members -----------------------------------------------------------------


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    joined_at: datetime


# --- Loans -------------------------------------------------------------------


class LoanCreate(BaseModel):
    book_id: int
    member_id: int


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    due_date: date
    returned_at: datetime | None


# --- Reports -----------------------------------------------------------------


class OverdueLoan(BaseModel):
    loan_id: int
    book_title: str
    member_name: str
    member_email: str
    due_date: date
    days_overdue: int


class PopularBook(BaseModel):
    book_id: int
    title: str
    author: str
    times_borrowed: int
