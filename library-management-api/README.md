# Library Management API

A REST API for running a small library, built with **FastAPI** and **MySQL**. Librarians can add books and members, lend and return books, and run reports such as overdue loans and the most popular books. The project also includes a set of hand-written SQL queries against the same database.

## Features

- Add, search, update and delete **books** (search by title or author, filter to available books, pagination)
- Register **members** and view each member's borrowing history
- **Borrow and return** books, with these rules:
  - a book can only be borrowed if a copy is available
  - a member can have at most 3 books at a time
  - a member can't borrow two copies of the same book
  - books are due back after 14 days
- **Reports:** overdue loans (with days overdue) and most borrowed books, built with SQL joins and `GROUP BY`
- **CHECK constraints** in the database so copy counts can never go negative or above the total
- [`sql/example_queries.sql`](sql/example_queries.sql): seven MySQL queries using `JOIN`, `LEFT JOIN`, `GROUP BY`, `HAVING` and date functions, plus [`sql/sample_data.sql`](sql/sample_data.sql) to try them on
- Database migrations with **Alembic**
- **17 automated tests** with pytest
- Runs with **Docker Compose** (API + MySQL)

## Tech stack

Python · FastAPI · SQLAlchemy · MySQL · Alembic · Pydantic · pytest · Docker

## Project structure

```
app/
  main.py            Creates the FastAPI app and includes the routers
  config.py          Settings (database URL, loan length, loan limit)
  database.py        Database connection and session
  models.py          Database tables (Book, Member, Loan)
  schemas.py         Request and response models
  routers/
    books.py         /books endpoints
    members.py       /members endpoints
    loans.py         /loans endpoints (borrow and return)
    reports.py       /reports endpoints
sql/
  sample_data.sql      Example books, members and loans
  example_queries.sql  Hand-written MySQL queries
alembic/             Database migrations
tests/               pytest tests
```

## Database design

```
books ──< loans >── members
```

| Table | Purpose |
|---|---|
| `books` | Title, author, unique ISBN, total copies and how many are available |
| `members` | Name and unique email |
| `loans` | Which member has which book, when it's due, and when it was returned (`NULL` while still borrowed) |

`books.title` and `books.author` are indexed for searching, and `loans` has an index on `(member_id, returned_at)` because "what does this member have right now?" is checked every time someone borrows a book.

## API endpoints

Full interactive documentation is available at `/docs` once the app is running.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/books` | List books (`search`, `available_only`, `skip`, `limit`) |
| GET | `/books/{id}` | Get one book |
| POST | `/books` | Add a book |
| PATCH | `/books/{id}` | Update a book (including number of copies) |
| DELETE | `/books/{id}` | Delete a book (only if it has never been borrowed) |
| POST | `/members` | Register a member |
| GET | `/members` | List members |
| GET | `/members/{id}` | Get one member |
| GET | `/members/{id}/loans` | A member's loans (`current_only=true` for unreturned) |
| POST | `/loans` | Borrow a book (`book_id`, `member_id`) |
| POST | `/loans/{id}/return` | Return a book |
| GET | `/loans` | List loans (`current_only=true` for unreturned) |
| GET | `/reports/overdue` | Loans past their due date |
| GET | `/reports/popular-books` | Most borrowed books |

Example: borrowing a book

```bash
curl -X POST http://localhost:8000/loans \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "member_id": 2}'
```

## Getting started

### With Docker (easiest)

```bash
docker compose up --build
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

To load the sample data and try the SQL queries:

```bash
docker compose exec -T db mysql -uapp -papp library < sql/sample_data.sql
docker compose exec -T db mysql -uapp -papp library < sql/example_queries.sql
```

### Without Docker

You need Python 3.11+ and a MySQL database.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env               # then edit DATABASE_URL
alembic upgrade head               # create the tables
uvicorn app.main:app --reload
```

## Running the tests

```bash
pytest
```

The tests use a temporary in-memory SQLite database, so MySQL isn't needed. They cover adding and searching books, every borrowing rule, returning books, member history, and both reports. The GitHub Actions workflow also runs them against a real MySQL database on every push.

## What I learned

- Designing a relational database and choosing certain elements (e.g., foreign keys, unique columns) based on how the data ia actually queried
- Adding a `NULL` column (`returned_at`) to differentiate past loans from current loans
- Adding `CHECK` constraints so that invalid data is blocked at the database level (and not just the API level)
- Writing reports (both as raw SQL and with SQLAlchemy) with `JOIN`, `GROUP BY`, `COUNT` and `HAVING` 
- Turning business rules (like loan limits and availability) into clear and concise validation with helpful error messages
- Writing flexible pytest tests for each rule that run against both SQLite and MySQL

## Future improvements

- Add a staff login so that only librarians can add books or record loans
- Let members reserve a book that's currently checked out and then receive it when it's returned
- Calculate late fees for books that are overdue
- Prevent two librarians from lending the last copy at the exact same moment (e.g., by locking the book row during checkout)
- Allow renewing a loan in order to extend the due date
