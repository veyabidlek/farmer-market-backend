from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import get_pending_farmers, approve_farmer, reject_farmer, disable_user, enable_user, authenticate_user, list_non_admin_users, delete_user
from database import get_db
from schemas import LoginRequest, UserResponse
from dependencies import create_access_token, get_current_user
from models import User
from typing import List

router = APIRouter()


@router.post("/login")
def login_admin(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.email, login_request.password)
    if user is None or not user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    access_token = create_access_token({"sub": user.email, "role": "admin" if user.is_admin else "user"})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/farmers/pending")
def list_pending_farmers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return get_pending_farmers(db)


@router.post("/farmers/{farmer_id}/approve")
def approve_farmer_account(farmer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return approve_farmer(db, farmer_id)


@router.post("/farmers/{farmer_id}/reject")
def reject_farmer_account(farmer_id: int, reason: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return reject_farmer(db, farmer_id, reason)


@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException("You are not admin")
    return list_non_admin_users(db)


@router.delete("/users/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not admin")
    delete_user(db, user_id)
    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/disable")
def disable_account(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return disable_user(db, user_id)


@router.post("/users/{user_id}/enable")
def enable_account(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return enable_user(db, user_id)
