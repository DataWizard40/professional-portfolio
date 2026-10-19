"""Create an admin user from the command line.

Usage:
    python create_admin.py admin@example.com yourpassword
"""

import sys

from sqlalchemy import select

from app.auth import hash_password
from app.database import SessionLocal
from app.models import User


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    email, password = sys.argv[1].lower(), sys.argv[2]
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, hashed_password=hash_password(password))
            db.add(user)
        user.is_admin = True
        db.commit()
        print(f"{email} is now an admin")
    finally:
        db.close()


if __name__ == "__main__":
    main()
