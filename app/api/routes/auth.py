from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.pydantic_models import UserOut, Token, LoginRequest, RegisterRequest
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.schema import User, Organization
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Operation not permitted"
            )
        return user

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    try:
        org = Organization(
            name=data.orgName,
            industry=data.industry,
            size=data.orgSize
        )
        db.add(org)
        db.flush() # get org.id without committing

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.adminName,
            phone=data.phone,
            org_id=org.id,
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/sso/{provider}")
def sso_login(provider: str):
    supported = ["microsoft", "google"]
    if provider not in supported:
        raise HTTPException(status_code=400, detail=f"Unsupported SSO provider: {provider}")
    
    # SSO OAuth2 flow not yet implemented — return 501
    raise HTTPException(
        status_code=501,
        detail=f"{provider.capitalize()} SSO is not yet configured on this instance. Contact your administrator."
    )

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
