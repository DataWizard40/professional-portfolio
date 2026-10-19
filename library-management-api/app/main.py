from fastapi import FastAPI

from app.routers import books, loans, members, reports

app = FastAPI(
    title="Library Management API",
    description="Manage a library's books and members, lend and return books, and run reports.",
    version="1.0.0",
)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)
app.include_router(reports.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}
