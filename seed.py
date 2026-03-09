"""
Run this once after deploying to seed your database with lenders and a default admin.
Usage: python seed.py
"""
from database import SessionLocal, engine
from models import Base, Lender, AdminUser
import bcrypt

Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def seed():
    db = SessionLocal()

    # ── Seed Lenders ──
    existing_lenders = db.query(Lender).count()
    if existing_lenders == 0:
        lenders = [
            Lender(name="Apex Capital", lender_type="Private Credit Fund", avatar_initials="AC",
                   color="#1a7a4a", appetite="low", min_risk="low", max_risk="low",
                   rate_min=8.0, rate_max=12.0, available_capital=15_000_000, total_deployed=48_000_000, total_deals=34),
            Lender(name="GroFund", lender_type="Development Finance", avatar_initials="GF",
                   color="#2255cc", appetite="low-med", min_risk="low", max_risk="med",
                   rate_min=9.0, rate_max=14.0, available_capital=22_000_000, total_deployed=91_000_000, total_deals=67),
            Lender(name="Highveld Partners", lender_type="Boutique Lender", avatar_initials="HP",
                   color="#b86c00", appetite="med", min_risk="med", max_risk="med",
                   rate_min=13.0, rate_max=18.0, available_capital=8_000_000, total_deployed=29_000_000, total_deals=21),
            Lender(name="Zenith Ventures", lender_type="Alternative Finance", avatar_initials="ZV",
                   color="#8b1a1a", appetite="high", min_risk="med", max_risk="high",
                   rate_min=18.0, rate_max=28.0, available_capital=5_000_000, total_deployed=17_000_000, total_deals=15),
            Lender(name="TerraFin", lender_type="Specialised Lender", avatar_initials="TF",
                   color="#5533aa", appetite="med-high", min_risk="low", max_risk="high",
                   rate_min=11.0, rate_max=22.0, available_capital=11_000_000, total_deployed=38_000_000, total_deals=29),
            Lender(name="Shoreline Capital", lender_type="Impact Investor", avatar_initials="SC",
                   color="#0e7490", appetite="low", min_risk="low", max_risk="med",
                   rate_min=7.0, rate_max=11.0, available_capital=30_000_000, total_deployed=120_000_000, total_deals=88),
        ]
        db.add_all(lenders)
        print(f"✓ Seeded {len(lenders)} lenders")
    else:
        print(f"  Lenders already exist, skipping")

    # ── Seed Default Admin ──
    existing_admin = db.query(AdminUser).filter(AdminUser.email == "admin@capflow.co.za").first()
    if not existing_admin:
        admin = AdminUser(
            name="CapFlow Admin",
            email="admin@capflow.co.za",
            password_hash=hash_password("CapFlow2026!"),
            role="superadmin"
        )
        db.add(admin)
        print("✓ Created default admin: admin@capflow.co.za / CapFlow2026!")
        print("  ⚠️  Change this password immediately after first login!")
    else:
        print("  Admin already exists, skipping")

    db.commit()
    db.close()
    print("\n✅ Seed complete!")

if __name__ == "__main__":
    seed()
