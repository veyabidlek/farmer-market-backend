from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Delivery

router = APIRouter()

@router.get("/deliveries/{order_id}")
def track_delivery(order_id: int, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    return {
        "order_id": delivery.order_id,
        "status": delivery.status,
        "delivery_address": delivery.delivery_address,
        "date": delivery.date
    }
