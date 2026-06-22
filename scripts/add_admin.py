import hashlib
from app.core.database import SessionLocal
from app.models.schema import User

def add_admin():
    db = SessionLocal()
    email = "admin@camfind.ai"
    password = "admin"
    
    # Check if exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        user = User(
            email=email,
            password_hash=hashed_pw,
            role="admin"
        )
        db.add(user)
        db.commit()
        print(f"Created admin user: {email} / {password}")
    else:
        print(f"Admin user already exists: {email}")
        
    db.close()

if __name__ == "__main__":
    add_admin()
