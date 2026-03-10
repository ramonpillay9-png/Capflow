from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ApplicationCreate(BaseModel):
    business_name: str
    registration_number: str
    industry: str
    years_in_operation: int
    annual_turnover: float
    finance_amount: float
    finance_purpose: str
    repayment_period: int
    contact_name: str
    contact_email: str
    contact_phone: str
    collateral: Optional[str] = None
    credit_score: Optional[int] = None

    class Config:
        orm_mode = True


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    risk_profile: Optional[str] = None

    class Config:
        orm_mode = True


class ApplicationOut(BaseModel):
    id: int
    business_name: str
    registration_number: str
    industry: str
    years_in_operation: int
    annual_turnover: float
    finance_amount: float
    finance_purpose: str
    repayment_period: int
    contact_name: str
    contact_email: str
    contact_phone: str
    collateral: Optional[str] = None
    credit_score: Optional[int] = None
    status: str
    risk_profile: Optional[str] = None
    reference_number: str
    created_at: datetime

    class Config:
        orm_mode = True


class LenderCreate(BaseModel):
    name: str
    risk_appetite: str
    min_rate: float
    max_rate: float
    available_capital: float

    class Config:
        orm_mode = True


class LenderOut(BaseModel):
    id: int
    name: str
    risk_appetite: str
    min_rate: float
    max_rate: float
    available_capital: float
    deployed_capital: float
    active: bool

    class Config:
        orm_mode = True


class LenderUpdate(BaseModel):
    risk_appetite: Optional[str] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    available_capital: Optional[float] = None
    active: Optional[bool] = None


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class StatusUpdate(BaseModel):
    status: str


class PaymentRelease(BaseModel):
    application_id: int
    lender_ids: List[int]
    amount: float
    fee_percentage: float = 2.5


class PaymentAssignmentOut(BaseModel):
    id: int
    application_id: int
    lender_id: int
    amount: float
    fee: float
    net_amount: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
