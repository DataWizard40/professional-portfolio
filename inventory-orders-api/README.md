# Inventory & Orders API

A REST API for a small online store, built with **FastAPI** and **MySQL**. Admins manage the product catalog, and customers can create an account, log in, place orders and cancel them. Stock levels update automatically when orders are placed or cancelled.

## Features

- User registration and login with **JWT authentication** and hashed passwords (bcrypt)
- **Admin-only** routes for adding, editing and deleting products
- Product search by name, an "in stock only" filter, and pagination (`skip` / `limit`)
- Placing an order checks stock for every item and reduces it; if any item fails, **nothing is saved**
- Cancelling an order puts the items back in stock
- Each order stores the price at the time of purchase, so later price changes don't change old orders
- Customers can only see their own orders
- Input validation with Pydantic (e.g. no negative prices, passwords at least 8 characters)
- Database migrations with **Alembic**
- **20 automated tests** with pytest
- Runs with **Docker Compose** (API + MySQL)

## Tech stack

Python · FastAPI · SQLAlchemy · MySQL · Alembic · Pydantic · pytest · Docker

## Project structure

```
app/
  main.py          Creates the FastAPI app and includes the routers
  config.py        Settings loaded from environment variables
  database.py      Database connection and session
  models.py        Database tables (User, Product, Order, OrderItem)
  schemas.py       Request and response models
  auth.py          Password hashing, JWT tokens, login dependencies
  routers/
    auth.py        /auth endpoints
    products.py    /products endpoints
    orders.py      /orders endpoints
alembic/           Database migrations
tests/             pytest tests
create_admin.py    Script to create an admin user
```

## Database design

```
users ──< orders ──< order_items >── products
```

- A user has many orders; an order has many order items; each order item points to one product.
- `email` and `sku` are unique, and `products.name` is indexed to make searching faster.

## API endpoints

Full interactive documentation is available at `/docs` once the app is running.

| Method | Endpoint | Who can use it | Description |
|---|---|---|---|
| POST | `/auth/register` | Anyone | Create an account |
| POST | `/auth/login` | Anyone | Log in and get a token |
| GET | `/auth/me` | Logged in | Your account details |
| GET | `/products` | Anyone | List products (`search`, `in_stock`, `skip`, `limit`) |
| GET | `/products/{id}` | Anyone | Get one product |
| POST | `/products` | Admin | Add a product |
| PATCH | `/products/{id}` | Admin | Update a product |
| DELETE | `/products/{id}` | Admin | Delete a product (only if it has never been ordered) |
| POST | `/orders` | Logged in | Place an order |
| GET | `/orders` | Logged in | List your orders |
| GET | `/orders/{id}` | Logged in | Get one of your orders |
| POST | `/orders/{id}/cancel` | Logged in | Cancel an order and restock the items |

## Getting started

### With Docker (easiest)

```bash
docker compose up --build
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

Create an admin account in a second terminal:

```bash
docker compose exec api python create_admin.py admin@example.com yourpassword
```

### Without Docker

You need Python 3.11+ and a MySQL database.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env               # then edit DATABASE_URL and SECRET_KEY
alembic upgrade head               # create the tables
uvicorn app.main:app --reload
```

## Running the tests

```bash
pytest
```

The tests use a temporary in-memory SQLite database, so MySQL isn't needed. They cover registration and login, admin permissions, product search and validation, stock updates, cancelling orders, and making sure a failed order doesn't change any stock. The GitHub Actions workflow also runs them against a real MySQL database on every push.

## What I learned

- How to structure a FastAPI project with routers, Pydantic schemas and SQLAlchemy models kept in separate files
- How JWT authentication works: hashing passwords with bcrypt, creating tokens on login, and checking them with a FastAPI dependency
- Using database transactions so that an order with one bad item doesn't leave stock half-updated
- Designing related tables with foreign keys and unique constraints, and managing schema changes with Alembic migrations
- Writing tests with pytest and FastAPI's `TestClient`, using a separate test database so tests don't touch real data
- Running an app and its database together with Docker Compose

## Future improvements

- **Handle simultaneous orders safely.** If two customers order the last item at exactly the same moment, both requests could read the same stock level. Locking the product row while an order is placed (`SELECT ... FOR UPDATE`) would prevent this.
- Add an order status workflow for admins (e.g. paid → shipped)
- Return the total count with paginated results so a frontend can show page numbers
- Add refresh tokens so users don't have to log in again every hour
- Build a simple frontend that uses this API
