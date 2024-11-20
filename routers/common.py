from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from crud import list_categories
from database import get_db
from schemas import CategoryResponse
from typing import List


router = APIRouter()


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories_endpoint(db: Session = Depends(get_db)):
    return list_categories(db)
