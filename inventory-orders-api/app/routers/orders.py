from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Order, OrderItem, Product, User
from app.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


def get_my_order_or_404(db: Session, order_id: int, user: User) -> Order:
    order = db.get(Order, order_id)
    # Users can only see their own orders.
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Place an order. Stock is checked and reduced for every item.

    All changes are saved together with one commit at the end. If any item fails
    (unknown product or not enough stock), nothing is saved.
    """
    order = Order(user_id=current_user.id, status="placed")
    total = Decimal("0.00")

    for item in order_in.items:
        product = db.get(Product, item.product_id)
        if product is None:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.quantity < item.quantity:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name} (only {product.quantity} left)",
            )

        product.quantity -= item.quantity
        order.items.append(
            OrderItem(product_id=product.id, quantity=item.quantity, unit_price=product.price)
        )
        total += product.price * item.quantity

    order.total = total
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderOut])
def list_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(Order).where(Order.user_id == current_user.id).order_by(Order.id.desc())
    return db.scalars(query).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_order_or_404(db, order_id, current_user)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an order and put the items back in stock."""
    order = get_my_order_or_404(db, order_id, current_user)
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Order is already cancelled")

    for item in order.items:
        item.product.quantity += item.quantity
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order
