from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ProductCreate, FarmerCreate, LoginRequest, FarmerResponse, OrderResponse
from crud import create_product, get_farmer_products, update_product, delete_product, create_farmer, authenticate_user, get_farmer_by_user_id, get_product_by_id
from database import get_db
from dependencies import create_access_token, get_current_user
from models import User, OrderItem, Order
from typing import List

router = APIRouter()


@router.post("/register")
def register_farmer(farmer_data: FarmerCreate, db: Session = Depends(get_db)):
    create_farmer(db, farmer_data)
    return {"message": "Farmer registration successful. Pending admin approval."}


@router.post("/login")
def login_farmer(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.email, login_request.password)
    if user is None:
        raise HTTPException(status_code=403, detail="User does not exist")
    farmer = get_farmer_by_user_id(db, user.id)
    if farmer is None:
        raise HTTPException(status_code=403, detail="Farmer does not exist")
    if farmer.pending:
        raise HTTPException(status_code=403, detail="farmer is pending")
    access_token = create_access_token({"sub": user.email, "role": "admin" if user.is_admin else "user"})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user", response_model=FarmerResponse)
def get_farmer_info(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farmer = get_farmer_by_user_id(db, current_user.id)
    if farmer is None:
        raise HTTPException(status_code=403, detail="User is not farmer")
    return farmer


@router.post("/products")
def add_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farmer = get_farmer_by_user_id(db, current_user.id)
    if farmer is None:
        raise HTTPException(status_code=403, detail="User is not farmer")
    product_data = product.dict()
    product_data["farmer_id"] = farmer.id
    return create_product(db, product_data)


@router.get("/products")
def list_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farmer = get_farmer_by_user_id(db, current_user.id)
    return get_farmer_products(db, farmer.id)


@router.put("/products/{product_id}")
def update_product_details(product_id: int, product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farmer = get_farmer_by_user_id(db, current_user.id)
    product_for_update = get_product_by_id(db, product_id)
    if product_for_update.farmer_id != farmer.id:
        raise HTTPException(status_code=403, detail="You are not owner of the product")
    return update_product(db, product_id, product)


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    farmer = get_farmer_by_user_id(db, current_user.id)
    product_for_update = get_product_by_id(db, product_id)
    if product_for_update.farmer_id != farmer.id:
        raise HTTPException(status_code=403, detail="You are not owner of the product")
    return delete_product(db, product_id)


@router.get("/orders", response_model=List[OrderResponse])
def get_farmer_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farmer = get_farmer_by_user_id(db, current_user.id)
    if not farmer:
        raise HTTPException(status_code=403, detail="User is not a farmer")
    orders = db.query(Order).join(OrderItem).filter(OrderItem.product.has(farmer_id=farmer.id)).all()
    return orders


@router.put("/orders/{id}/status", response_model=OrderResponse)
def update_order_status(id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.is_admin or (current_user.is_farmer and order.items[0].product.farmer.user_id == current_user.id):
        order.status = status
        db.commit()
        db.refresh(order)
        return order
    raise HTTPException(status_code=403, detail="Unauthorized to update order status")