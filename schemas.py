from pydantic import BaseModel, field_validator
from typing import Optional
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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


class LenderOut(BaseModel):
    id: int
    name: str
    risk_appetite: str
    min_rate: float
    max_rate: float
    available_capital: float
    deployed_capital: float
    active: bool

    model_config = {"from_attributes": True}


class LenderUpdate(BaseModel):
    risk_appetite: Optional[str] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    available_capital: Optional[float] = None
    active: Optional[bool] = None


class AdminLogin(BaseModel):
    username: str
    password: str


class StatusUpdate(BaseModel):
    status: str


class PaymentRelease(BaseModel):
    application_id: int
    lender_ids: list[int]
    amount: float
    fee_percentage: float = 2.5
