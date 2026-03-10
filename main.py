from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import random
import string

from database import get_db, engine
from models import Base, Application, Lender, AdminUser, PaymentAssignment
from schemas import (
    ApplicationCreate, ApplicationOut, ApplicationUpdate,
    LenderCreate, LenderOut, LenderUpdate,
    AdminLogin, StatusUpdate, PaymentRelease, Token
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CapFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_reference():
    return "CF-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def calculate_risk(application: Application) -> str:
    score = 0
    if application.years_in_operation >= 3:
        score += 2
    if application.annual_turnover >= application.finance_amount * 2:
        score += 2
    if application.credit_score and application.credit_score >= 650:
        score += 2
    if application.collateral:
        score += 1
    if score >= 5:
        return "low"
    elif score >= 3:
        return "medium"
    else:
        return "high"


@app.get("/")
def root():
    return {"message": "CapFlow API is running"}


@app.post("/api/apply", response_model=ApplicationOut)
def apply_for_finance(application: ApplicationCreate, db: Session = Depends(get_db)):
    db_app = Application(
        **application.dict(),
        status="pending",
        reference_number=generate_reference(),
        created_at=datetime.utcnow()
    )
    db_app.risk_profile = calculate_risk(db_app)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app


@app.get("/api/applications", response_model=List[ApplicationOut])
def get_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.created_at.desc()).all()


@app.get("/api/applications/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@app.patch("/api/applications/{app_id}/status")
def update_status(app_id: int, update: StatusUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = update.status
    db.commit()
    return {"message": "Status updated", "status": update.status}


@app.post("/api/applications/{app_id}/release-payment")
def release_payment(app_id: int, payment: PaymentRelease, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    fee = payment.amount * (payment.fee_percentage / 100)
    net = payment.amount - fee
    for lender_id in payment.lender_ids:
        assignment = PaymentAssignment(
            application_id=app_id,
            lender_id=lender_id,
            amount=payment.amount / len(payment.lender_ids),
            fee=fee / len(payment.lender_ids),
            net_amount=net / len(payment.lender_ids),
            status="released",
            created_at=datetime.utcnow()
        )
        db.add(assignment)
    app.status = "funded"
    db.commit()
    return {"message": "Payment released", "net_amount": net, "fee": fee}


@app.get("/api/lenders", response_model=List[LenderOut])
def get_lenders(db: Session = Depends(get_db)):
    return db.query(Lender).all()


@app.post("/api/lenders", response_model=LenderOut)
def create_lender(lender: LenderCreate, db: Session = Depends(get_db)):
    db_lender = Lender(**lender.dict(), deployed_capital=0, active=True)
    db.add(db_lender)
    db.commit()
    db.refresh(db_lender)
    return db_lender


@app.patch("/api/lenders/{lender_id}", response_model=LenderOut)
def update_lender(lender_id: int, update: LenderUpdate, db: Session = Depends(get_db)):
    lender = db.query(Lender).filter(Lender.id == lender_id).first()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    for key, value in update.dict(exclude_none=True).items():
        setattr(lender, key, value)
    db.commit()
    db.refresh(lender)
    return lender


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Application).count()
    pending = db.query(Application).filter(Application.status == "pending").count()
    approved = db.query(Application).filter(Application.status == "approved").count()
    funded = db.query(Application).filter(Application.status == "funded").count()
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "funded": funded
    }


@app.post("/api/admin/login")
def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    import bcrypt
    admin = db.query(AdminUser).filter(
        (AdminUser.username == credentials.username) |
        (AdminUser.email == credentials.username)
    ).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        # Try password_hash field first (used by seed.py)
        stored = admin.password_hash or admin.password
        if stored and bcrypt.checkpw(credentials.password.encode(), stored.encode()):
            return {"message": "Login successful", "username": admin.email or admin.username}
    except Exception as e:
        # Fallback plain text check
        stored = admin.password_hash or admin.password
        if stored == credentials.password:
            return {"message": "Login successful", "username": admin.email or admin.username}
    raise HTTPException(status_code=401, detail="Invalid credentials")
