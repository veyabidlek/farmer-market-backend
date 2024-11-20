from fastapi import APIRouter, Depends
from schemas import UserResponse
from dependencies import get_current_user
from models import User

router = APIRouter()


@router.get("/user", response_model=UserResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user
