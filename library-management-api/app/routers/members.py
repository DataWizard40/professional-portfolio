from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Loan, Member
from app.schemas import LoanOut, MemberCreate, MemberOut

router = APIRouter(prefix="/members", tags=["members"])


def get_member_or_404(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def add_member(member_in: MemberCreate, db: Session = Depends(get_db)):
    email = member_in.email.lower()
    if db.scalar(select(Member).where(Member.email == email)):
        raise HTTPException(status_code=400, detail="A member with this email already exists")

    member = Member(name=member_in.name, email=email)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("", response_model=list[MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.scalars(select(Member).order_by(Member.name)).all()


@router.get("/{member_id}", response_model=MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return get_member_or_404(db, member_id)


@router.get("/{member_id}/loans", response_model=list[LoanOut])
def member_loans(member_id: int, current_only: bool = False, db: Session = Depends(get_db)):
    """A member's borrowing history, newest first. Use current_only=true for unreturned books."""
    get_member_or_404(db, member_id)
    query = select(Loan).where(Loan.member_id == member_id)
    if current_only:
        query = query.where(Loan.returned_at.is_(None))
    return db.scalars(query.order_by(Loan.id.desc())).all()
