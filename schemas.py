from pydantic import BaseModel, EmailStr
from typing import Optional


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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int
    description: Optional[str] = None
    category_id: int


class ProductResponse(ProductCreate):
    farmer: FarmerResponse


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
