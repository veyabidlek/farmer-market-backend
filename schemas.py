from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    phone_number: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool
    is_buyer: bool
    is_farmer: bool

    class Config:
        orm_mode = True

# Farmer schemas
class FarmerCreate(UserCreate):
    farm_address: str
    farm_size: float

class FarmerResponse(BaseModel):
    id: int
    farm_address: str
    farm_size: float
    user: UserResponse

    class Config:
        orm_mode = True

# Buyer schemas
class BuyerCreate(UserCreate):
    address: str
    payment_method: str

class BuyerResponse(BaseModel):
    id: int
    address: str
    payment_method: str
    user: UserResponse

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    image_url: str
    name: str
    price: float
    quantity: int
    description: Optional[str] = None
    category_id: int

class ProductResponse(BaseModel):
    id: int
    image_url: str
    name: str
    price: float
    quantity: int
    description: Optional[str] = None
    category_id: int
    farmer: FarmerResponse

    class Config:
        orm_mode = True

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    buyer_id: Optional[int] = None
    date: datetime
    amount: float
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    date: datetime
    status: str
    amount: float
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PaymentRequest(BaseModel):
    order_id: int
    amount: float
    payment_method: str
    payment_reference: Optional[str] = None

# Chat schemas
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True

class ConversationBase(BaseModel):
    pass

class ConversationCreate(ConversationBase):
    farmer_id: int
    buyer_id: int

class ConversationResponse(BaseModel):
    id: int
    farmer_id: int
    buyer_id: int
    messages: List[MessageResponse] = []

    class Config:
        orm_mode = True
