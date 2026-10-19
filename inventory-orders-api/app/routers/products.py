from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models import OrderItem, Product
from app.schemas import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("", response_model=list[ProductOut])
def list_products(
    search: str | None = None,
    in_stock: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List products, optionally searching by name and hiding sold-out items."""
    query = select(Product)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if in_stock:
        query = query.where(Product.quantity > 0)
    query = query.order_by(Product.name).offset(skip).limit(limit)
    return db.scalars(query).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(db, product_id)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    if db.scalar(select(Product).where(Product.sku == product_in.sku)):
        raise HTTPException(status_code=400, detail="A product with this SKU already exists")

    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    product = get_product_or_404(db, product_id)
    # exclude_unset=True means fields the client didn't send are left alone.
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    product = get_product_or_404(db, product_id)
    # Keep order history intact: products that were ordered can't be deleted.
    if db.scalar(select(OrderItem).where(OrderItem.product_id == product_id).limit(1)):
        raise HTTPException(
            status_code=400,
            detail="This product has been ordered and can't be deleted. Set quantity to 0 instead.",
        )
    db.delete(product)
    db.commit()
