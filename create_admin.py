from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

# Predefined admin credentials
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "admin"


def create_admin():
    db: Session = SessionLocal()

    admin = db.query(User).filter(User.email == ADMIN_EMAIL, User.is_admin == True).first()
    if admin:
        print("Admin user already exists.")
        return

    new_admin = User(
        name="Admin",
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        is_admin=True,
        is_buyer=False,
        is_farmer=False
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    print(f"Admin user created with email: {ADMIN_EMAIL}")


if __name__ == "__main__":
    create_admin()
