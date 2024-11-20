from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from schemas import Token, UserResponse
from dependencies import get_current_user, create_access_token
from crud import authenticate_user
from models import User
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.get("/user", response_model=UserResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}