from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


# ── APPLICATIONS ──

class ApplicationCreate(BaseModel):
    registered_name: str
    trading_name: Optional[str] = None
    registration_number: Optional[str] = None
    sector: Optional[str] = None
    years_in_operation: Optional[str] = None
    num_employees: Optional[str] = None
    contact_person: Optional[str] = None
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    amount: float
    finance_type: Optional[str] = None
    repayment_term: Optional[str] = None
    annual_turnover: Optional[float] = None
    credit_score: Optional[str] = None
    collateral: Optional[str] = None
    purpose: Optional[str] = None
    risk_profile: Optional[str] = "med"

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None
    risk_profile: Optional[str] = None

class LenderAssignmentOut(BaseModel):
    lender_id: int
    amount: float
    released_at: Optional[datetime]
    class Config:
        from_attributes = True

class ApplicationOut(BaseModel):
    id: int
    reference: str
    registered_name: str
    trading_name: Optional[str]
    registration_number: Optional[str]
    sector: Optional[str]
    years_in_operation: Optional[str]
    num_employees: Optional[str]
    contact_person: Optional[str]
    email: str
    phone: Optional[str]
    address: Optional[str]
    amount: float
    finance_type: Optional[str]
    repayment_term: Optional[str]
    annual_turnover: Optional[float]
    credit_score: Optional[str]
    collateral: Optional[str]
    purpose: Optional[str]
    risk_profile: Optional[str]
    status: str
    admin_notes: Optional[str]
    submitted_at: datetime
    updated_at: Optional[datetime]
    funded_at: Optional[datetime]
    lender_assignments: List[LenderAssignmentOut] = []
    class Config:
        from_attributes = True


# ── LENDERS ──

class LenderCreate(BaseModel):
    name: str
    lender_type: Optional[str] = None
    avatar_initials: Optional[str] = None
    color: Optional[str] = "#1a7a4a"
    appetite: Optional[str] = "med"
    min_risk: Optional[str] = "low"
    max_risk: Optional[str] = "med"
    rate_min: Optional[float] = None
    rate_max: Optional[float] = None
    available_capital: Optional[float] = 0
    total_deployed: Optional[float] = 0
    total_deals: Optional[int] = 0

class LenderUpdate(BaseModel):
    name: Optional[str] = None
    lender_type: Optional[str] = None
    appetite: Optional[str] = None
    min_risk: Optional[str] = None
    max_risk: Optional[str] = None
    rate_min: Optional[float] = None
    rate_max: Optional[float] = None
    available_capital: Optional[float] = None
    is_active: Optional[bool] = None

class LenderOut(BaseModel):
    id: int
    name: str
    lender_type: Optional[str]
    avatar_initials: Optional[str]
    color: Optional[str]
    appetite: Optional[str]
    min_risk: Optional[str]
    max_risk: Optional[str]
    rate_min: Optional[float]
    rate_max: Optional[float]
    available_capital: Optional[float]
    total_deployed: Optional[float]
    total_deals: Optional[int]
    is_active: bool
    class Config:
        from_attributes = True


# ── AUTH ──

class AdminUserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "admin"

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    name: str
    email: str
    role: str


# ── PAYMENTS ──

class PaymentRelease(BaseModel):
    lender_ids: List[int]
    amount_per_lender: Optional[Dict[str, float]] = {}


# ── STATS ──

class DashboardStats(BaseModel):
    total: int
    pending: int
    approved: int
    funded: int
    declined: int
    total_funded_amount: float
