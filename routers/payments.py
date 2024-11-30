from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Payment, Order, Delivery
from schemas import PaymentRequest
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ProductCreate, FarmerCreate, LoginRequest, FarmerResponse, OrderResponse
from crud import create_product, get_farmer_products, update_product, delete_product, create_farmer, authenticate_user, get_farmer_by_user_id, get_product_by_id
from database import get_db
from dependencies import create_access_token, get_current_user
from models import User, OrderItem, Order
from typing import List



router = APIRouter()

@router.post("/payments")
def process_payment(payment: PaymentRequest, db: Session = Depends(get_db)):
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid payment amount")
    
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payment_record = Payment(
        order_id=payment.order_id,
        date=datetime.utcnow(),
        amount=payment.amount,
        status="Processed",
    )
    db.add(payment_record)
    db.commit()
    db.refresh(payment_record)

    delivery = Delivery(
        order_id=order.id,
        date=datetime.utcnow(),
        status="Pending",
        delivery_address="123 Example Address, City, Country",
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return {
        "message": "Payment processed successfully, delivery initiated",
        "payment_id": payment_record.id,
        "delivery_id": delivery.id
    }
