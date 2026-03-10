from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
from datetime import datetime


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String)
    registration_number = Column(String)
    industry = Column(String)
    years_in_operation = Column(Integer)
    annual_turnover = Column(Float)
    finance_amount = Column(Float)
    finance_purpose = Column(String)
    repayment_period = Column(Integer)
    contact_name = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    collateral = Column(String, nullable=True)
    credit_score = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    risk_profile = Column(String, nullable=True)
    reference_number = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Lender(Base):
    __tablename__ = "lenders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    risk_appetite = Column(String)
    min_rate = Column(Float)
    max_rate = Column(Float)
    available_capital = Column(Float)
    deployed_capital = Column(Float, default=0)
    active = Column(Boolean, default=True)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=True)
    role = Column(String, nullable=True)


class PaymentAssignment(Base):
    __tablename__ = "payment_assignments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer)
    lender_id = Column(Integer)
    amount = Column(Float)
    fee = Column(Float)
    net_amount = Column(Float)
    status = Column(String, default="released")
    created_at = Column(DateTime, default=datetime.utcnow)
