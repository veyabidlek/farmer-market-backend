from sqlalchemy.orm import Session
from models import User, Farmer, Product, Farm, Buyer, Category
from schemas import FarmerCreate, BuyerCreate


# User Operations
def create_user(db: Session, user_data):
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and user.password == password:  # Replace with password hashing logic
        return user
    return None


def get_current_user(db: Session, user_id: int):
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

    # Create and save the Farmer instance
    farmer = Farmer(user_id=user.id)
    db.add(farmer)
    db.flush()

    # Create and save the Farm instance
    farm = Farm(farmer_id=farmer.id, **farm_data)
    db.add(farm)

    # Commit the transaction
    db.commit()

    # Refresh the instances to reflect the database state
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
    farmer = db.query(Farmer).filter(Farmer.user_id==user_id).first()
    return farmer


def get_buyer_by_user_id(db: Session, user_id: int):
    buyer = db.query(Buyer).filter(Buyer.user_id==user_id).first()
    return buyer


# Admin Operations
def get_pending_farmers(db: Session):
    return db.query(Farmer).filter(Farmer.pending == True).all()


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
    """
    Fetch a user by their email address.
    """
    return db.query(User).filter(User.email == email).first()


def get_available_products(db: Session):
    """
    Fetch all available products.
    """
    return db.query(Product).filter(Product.quantity > 0).all()


def search_products(db: Session, query: str):
    """
    Search for products by name.
    """
    return db.query(Product).filter(Product.name.ilike(f"%{query}%")).all()


def filter_products(db: Session, price_range: str = None, category_id: int = None, farm_location: str = None):
    """
    Filter products by price range, category, and farm location.
    """
    query = db.query(Product)

    # Apply price range filter
    if price_range:
        min_price, max_price = map(float, price_range.split("-"))
        query = query.filter(Product.price >= min_price, Product.price <= max_price)

    # Apply category filter
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Apply farm location filter
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
