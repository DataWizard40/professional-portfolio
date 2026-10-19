"""Pydantic models that define what the API accepts and returns."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- Users -------------------------------------------------------------------


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Products ----------------------------------------------------------------


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=50)
    description: str | None = None
    price: Decimal = Field(ge=0, decimal_places=2)
    quantity: int = Field(ge=0)


class ProductUpdate(BaseModel):
    """All fields optional, so only the fields sent are changed."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    quantity: int | None = Field(default=None, ge=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    description: str | None
    price: Decimal
    quantity: int


# --- Orders ------------------------------------------------------------------


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total: Decimal
    created_at: datetime
    items: list[OrderItemOut]
