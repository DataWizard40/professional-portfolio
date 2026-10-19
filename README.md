# Backend Developer Portfolio

[![CI](https://github.com/DataWizard40/professional-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/DataWizard40/professional-portfolio/actions/workflows/ci.yml)

Hi! I'm an entry-level software developer focused on **back-end development with Python**. These projects show what I've been building with **FastAPI** and **MySQL**: REST APIs with authentication, relational database design, SQL queries, and automated tests.

## Projects

### [Inventory & Orders API](inventory-orders-api)

An API for a small online store. Admins manage products; customers register, log in, place orders and cancel them, and stock updates automatically.

**Highlights:** JWT login with hashed passwords, admin-only routes, orders saved in a single transaction, product search and pagination, 20 tests.

### [Library Management API](library-management-api)

An API for running a library: books, members, borrowing and returning, plus reports for overdue loans and popular books.

**Highlights:** relational database design with constraints and indexes, borrowing rules, SQL reports with `JOIN` and `GROUP BY`, a file of hand-written MySQL queries, 17 tests.

## Skills

| Area | What I used |
|---|---|
| Language | Python |
| Web framework | FastAPI, Pydantic |
| Databases | MySQL, SQL (joins, aggregation, constraints, indexes), SQLAlchemy, Alembic migrations |
| Security | Password hashing (bcrypt), JWT authentication |
| Testing | pytest, FastAPI TestClient |
| Tools | Git, GitHub Actions, Docker, Docker Compose |

## How the projects are set up

- Each project has its own folder, README, tests and Docker setup.
- **GitHub Actions** runs on every push: it checks code style, applies the database migrations to MySQL, and runs the tests against both SQLite and MySQL.
- Each README ends with **what I learned** and **what I'd improve next**.

## Running a project

```bash
cd inventory-orders-api        # or library-management-api
docker compose up --build
# then open http://localhost:8000/docs
```
