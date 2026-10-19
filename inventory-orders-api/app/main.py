from fastapi import FastAPI

from app.routers import auth, orders, products

app = FastAPI(
    title="Inventory & Orders API",
    description="Manage products and place orders, with user accounts and admin access.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}
