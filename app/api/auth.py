import hashlib
import hmac
import base64
import json
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import settings
from app.db.metadata import (
    get_db,
    get_user_by_email,
    get_user_by_username,
    create_user,
    User
)

router = APIRouter()

# Simple, reliable, zero-dependency signed JWT/Token mechanism
def hash_password(password: str) -> str:
    salt = settings.SECRET_KEY[:16].encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000).hex()

def verify_password(plain_password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(plain_password), hashed)

def create_access_token(user_id: int, email: str, username: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "username": username,
        "exp": int(time.time()) + (86400 * 7) # 7 days
    }
    header = {"alg": "HS256", "typ": "JWT"}
    b64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    b64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hmac.new(
        settings.SECRET_KEY.encode(),
        f"{b64_header}.{b64_payload}".encode(),
        hashlib.sha256
    ).digest()
    b64_sig = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{b64_header}.{b64_payload}.{b64_sig}"

def decode_access_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        b64_header, b64_payload, b64_sig = parts
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            f"{b64_header}.{b64_payload}".encode(),
            hashlib.sha256
        ).digest()
        actual_sig = base64.urlsafe_b64decode(b64_sig + "==")
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_data = json.loads(base64.urlsafe_b64decode(b64_payload + "==").decode())
        if payload_data.get("exp", 0) < time.time():
            return None
        return payload_data
    except Exception:
        return None

# Pydantic Schemas
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if get_user_by_username(db, req.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    hashed = hash_password(req.password)
    user = create_user(db, req.username, req.email, hashed)
    token = create_access_token(user.id, user.email, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Allow login by email or username
    user = get_user_by_email(db, req.email) or get_user_by_username(db, req.email)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    token = create_access_token(user.id, user.email, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@router.get("/me")
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user_by_email(db, payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user.to_dict()}

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
