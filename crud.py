from sqlalchemy.orm import Session, joinedload
from models import User, Farmer, Product, Farm, Buyer, Category, Order, OrderItem, Conversation, Message
from schemas import (
    UserCreate,
    BuyerCreate,
    FarmerCreate,
    ProductCreate,
    OrderCreate
)
from datetime import datetime

# User Operations
def create_user(db: Session, user_data):
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and user.password == password:
        return user
    return None

def get_current_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_farmer(db: Session, farmer_data: FarmerCreate):
    farm_data = {
        "address": farmer_data.farm_address,
        "size": farmer_data.farm_size
    }
    user_data = farmer_data.dict()
    user_data.pop("farm_address")
    user_data.pop("farm_size")
    user_data["is_farmer"] = True
    user = User(**user_data)
    db.add(user)
    db.flush()

    farmer = Farmer(user_id=user.id)
    db.add(farmer)
    db.flush()

    farm = Farm(farmer_id=farmer.id, **farm_data)
    db.add(farm)

    db.commit()

    db.refresh(user)
    db.refresh(farmer)
    db.refresh(farm)

    return {"user": user, "farmer": farmer, "farm": farm}

def create_buyer(db: Session, buyer_data: BuyerCreate):
    user_data = buyer_data.dict()
    user_data["is_buyer"] = True

    buyer_info = {
        "address": user_data.pop("address"),
        "payment_method": user_data.pop("payment_method")
    }

    user = User(**user_data)
    db.add(user)
    db.flush()

    buyer = Buyer(user_id=user.id, **buyer_info)
    db.add(buyer)

    db.commit()

    db.refresh(user)
    db.refresh(buyer)

    return {"user": user, "buyer": buyer}

def get_farmer_by_user_id(db: Session, user_id: int):
    return db.query(Farmer).filter(Farmer.user_id == user_id).first()

def get_buyer_by_user_id(db: Session, user_id: int):
    return db.query(Buyer).filter(Buyer.user_id == user_id).first()


# Admin Operations
def get_pending_farmers(db: Session):
    results = db.query(Farmer, User).join(User).filter(Farmer.pending == True).all()
    return [
        {
            "farmer_id": farmer.id,
            "user_id": user.id,
            "email": user.email,
            "pending": farmer.pending
        }
        for farmer, user in results
    ]

def approve_farmer(db: Session, farmer_id: int):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if farmer:
        farmer.pending = False
        db.commit()
        db.refresh(farmer)
        return farmer
    return None

def reject_farmer(db: Session, farmer_id: int, reason: str):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if farmer:
        db.delete(farmer)
        db.commit()
        return {"message": f"Farmer rejected: {reason}"}
    return None

def disable_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    return None

def enable_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user
    return None

# Product Operations
def create_product(db: Session, product_data):
    new_product = Product(**product_data)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def get_farmer_products(db: Session, farmer_id: int):
    return db.query(Product).filter(Product.farmer_id == farmer_id).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def update_product(db: Session, product_id: int, product_data):
    product = get_product_by_id(db, product_id)
    if product:
        for key, value in product_data.dict().items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product
    return None

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    return None

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_available_products(db: Session):
    return db.query(Product).filter(Product.quantity > 0).all()

def search_products(db: Session, query: str):
    return db.query(Product).filter(Product.name.ilike(f"%{query}%")).all()

def filter_products(db: Session, price_range: str = None, category_id: int = None, farm_location: str = None):
    query = db.query(Product)

    if price_range:
        min_price, max_price = map(float, price_range.split("-"))
        query = query.filter(Product.price >= min_price, Product.price <= max_price)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if farm_location:
        query = query.join(Product.farmer).filter(Product.farmer.address.ilike(f"%{farm_location}%"))

    return query.all()

def list_categories(db: Session):
    return db.query(Category).all()

def list_non_admin_users(db: Session):
    return db.query(User).filter(User.is_admin == False).all()

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    db.delete(user)
    db.commit()

def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def create_order(db: Session, order_data: OrderCreate):
    order = Order(
        buyer_id=order_data.buyer_id,
        date=order_data.date,
        status='pending',
        amount=order_data.amount
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in order_data.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    return order

# Chat operations
def get_conversation(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_or_create_conversation(db: Session, farmer_id: int, buyer_id: int):
    conversation = db.query(Conversation).filter(
        Conversation.farmer_id == farmer_id,
        Conversation.buyer_id == buyer_id
    ).first()
    if conversation:
        return conversation
    else:
        conversation = Conversation(farmer_id=farmer_id, buyer_id=buyer_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

def create_message(db: Session, conversation_id: int, sender_id: int, content: str):
    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        timestamp=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_conversations_for_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user.is_farmer:
        farmer = get_farmer_by_user_id(db, user_id)
        conversations = db.query(Conversation).options(joinedload(Conversation.messages)).filter(Conversation.farmer_id == farmer.id).all()
    elif user.is_buyer:
        buyer = get_buyer_by_user_id(db, user_id)
        conversations = db.query(Conversation).options(joinedload(Conversation.messages)).filter(Conversation.buyer_id == buyer.id).all()
    else:
        conversations = []
    return conversations
