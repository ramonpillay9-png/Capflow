from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)

    # Business info
    registered_name = Column(String, nullable=False)
    trading_name = Column(String)
    registration_number = Column(String)
    sector = Column(String)
    years_in_operation = Column(String)
    num_employees = Column(String)
    contact_person = Column(String)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)

    # Finance details
    amount = Column(Float, nullable=False)
    finance_type = Column(String)
    repayment_term = Column(String)
    annual_turnover = Column(Float)
    credit_score = Column(String)
    collateral = Column(String)
    purpose = Column(Text)

    # Risk & status
    risk_profile = Column(String, default="med")   # low / med / high
    status = Column(String, default="pending")      # pending / review / approved / funded / declined
    admin_notes = Column(Text)

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    funded_at = Column(DateTime, nullable=True)

    # Relationships
    lender_assignments = relationship("LenderAssignment", back_populates="application")


class Lender(Base):
    __tablename__ = "lenders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lender_type = Column(String)
    avatar_initials = Column(String)
    color = Column(String, default="#1a7a4a")

    # Risk appetite: low / low-med / med / med-high / high
    appetite = Column(String, default="med")
    min_risk = Column(String, default="low")
    max_risk = Column(String, default="med")

    rate_min = Column(Float)   # e.g. 8.0 (percent)
    rate_max = Column(Float)   # e.g. 12.0
    available_capital = Column(Float, default=0)
    total_deployed = Column(Float, default=0)
    total_deals = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    assignments = relationship("LenderAssignment", back_populates="lender")


class LenderAssignment(Base):
    __tablename__ = "lender_assignments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    lender_id = Column(Integer, ForeignKey("lenders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    released_at = Column(DateTime, default=datetime.utcnow)
    released_by = Column(Integer, ForeignKey("admin_users.id"))

    application = relationship("Application", back_populates="lender_assignments")
    lender = relationship("Lender", back_populates="assignments")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")   # admin / superadmin
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
