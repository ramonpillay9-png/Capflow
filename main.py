from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import os

from database import get_db, engine
from models import Base, Application, Lender, AdminUser, LenderAssignment
from schemas import (
    ApplicationCreate, ApplicationOut, ApplicationUpdate,
    LenderCreate, LenderOut, LenderUpdate,
    AdminUserCreate, LoginRequest, LoginResponse,
    PaymentRelease, DashboardStats
)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CapFlow API", version="1.0.0")

# ── CORS (allow your frontend domain) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "capflow-secret-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 12

security = HTTPBearer()

# ── AUTH HELPERS ──
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "email": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(AdminUser).filter(AdminUser.id == int(payload["sub"])).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_ref() -> str:
    import random
    return f"CF-{datetime.now().year}-{random.randint(1000,9999)}"

# ════════════════════════════════════
#  PUBLIC ROUTES (no auth needed)
# ════════════════════════════════════

@app.get("/")
def root():
    return {"message": "CapFlow API is running", "version": "1.0.0"}

@app.post("/api/apply", response_model=ApplicationOut, status_code=201)
def submit_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    """Business submits a finance application."""
    app_obj = Application(
        **payload.dict(),
        reference=generate_ref(),
        status="pending",
        submitted_at=datetime.utcnow()
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj

@app.get("/api/apply/{reference}", response_model=ApplicationOut)
def track_application(reference: str, db: Session = Depends(get_db)):
    """Business tracks their application by reference number."""
    app_obj = db.query(Application).filter(Application.reference == reference).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj

# ════════════════════════════════════
#  AUTH ROUTES
# ════════════════════════════════════

@app.post("/api/auth/register", response_model=LoginResponse)
def register_admin(payload: AdminUserCreate, db: Session = Depends(get_db)):
    """Register a new admin user (protect this endpoint in production!)."""
    existing = db.query(AdminUser).filter(AdminUser.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = AdminUser(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role or "admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, user.email)
    return {"token": token, "name": user.name, "email": user.email, "role": user.role}

@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Admin login."""
    user = db.query(AdminUser).filter(AdminUser.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user.id, user.email)
    return {"token": token, "name": user.name, "email": user.email, "role": user.role}

# ════════════════════════════════════
#  ADMIN — APPLICATIONS
# ════════════════════════════════════

@app.get("/api/admin/applications", response_model=List[ApplicationOut])
def list_applications(
    status: Optional[str] = None,
    risk: Optional[str] = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """List all applications with optional filters."""
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    if risk:
        q = q.filter(Application.risk_profile == risk)
    return q.order_by(Application.submitted_at.desc()).all()

@app.get("/api/admin/applications/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Not found")
    return app_obj

@app.patch("/api/admin/applications/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Update application status, notes, etc."""
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(app_obj, k, v)
    app_obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app_obj)
    return app_obj

@app.post("/api/admin/applications/{app_id}/release-payment", response_model=ApplicationOut)
def release_payment(
    app_id: int,
    payload: PaymentRelease,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Assign lenders and mark application as funded."""
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Not found")
    if app_obj.status != "approved":
        raise HTTPException(status_code=400, detail="Application must be approved before releasing payment")

    # Remove previous assignments
    db.query(LenderAssignment).filter(LenderAssignment.application_id == app_id).delete()

    # Create new assignments
    for lender_id in payload.lender_ids:
        lender = db.query(Lender).filter(Lender.id == lender_id).first()
        if lender:
            assignment = LenderAssignment(
                application_id=app_id,
                lender_id=lender_id,
                amount=payload.amount_per_lender.get(str(lender_id), app_obj.amount / len(payload.lender_ids)),
                released_at=datetime.utcnow(),
                released_by=admin.id
            )
            db.add(assignment)

    app_obj.status = "funded"
    app_obj.funded_at = datetime.utcnow()
    app_obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app_obj)
    return app_obj

@app.get("/api/admin/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Dashboard KPI stats."""
    total = db.query(Application).count()
    pending = db.query(Application).filter(Application.status == "pending").count()
    approved = db.query(Application).filter(Application.status == "approved").count()
    funded = db.query(Application).filter(Application.status == "funded").count()
    declined = db.query(Application).filter(Application.status == "declined").count()
    funded_apps = db.query(Application).filter(Application.status == "funded").all()
    total_funded = sum(a.amount for a in funded_apps)
    return {
        "total": total, "pending": pending, "approved": approved,
        "funded": funded, "declined": declined, "total_funded_amount": total_funded
    }

# ════════════════════════════════════
#  ADMIN — LENDERS
# ════════════════════════════════════

@app.get("/api/admin/lenders", response_model=List[LenderOut])
def list_lenders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(Lender).order_by(Lender.name).all()

@app.post("/api/admin/lenders", response_model=LenderOut, status_code=201)
def create_lender(payload: LenderCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    lender = Lender(**payload.dict())
    db.add(lender)
    db.commit()
    db.refresh(lender)
    return lender

@app.patch("/api/admin/lenders/{lender_id}", response_model=LenderOut)
def update_lender(lender_id: int, payload: LenderUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    lender = db.query(Lender).filter(Lender.id == lender_id).first()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(lender, k, v)
    db.commit()
    db.refresh(lender)
    return lender

@app.delete("/api/admin/lenders/{lender_id}", status_code=204)
def delete_lender(lender_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    lender = db.query(Lender).filter(Lender.id == lender_id).first()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    db.delete(lender)
    db.commit()
