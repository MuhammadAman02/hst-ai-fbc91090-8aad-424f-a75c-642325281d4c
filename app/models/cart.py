"""
Cart and order-related Pydantic models for API serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductResponse, ProductVariantResponse

class CartItemBase(BaseModel):
    """Base cart item model"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., ge=1, le=99)

class CartItemCreate(CartItemBase):
    """Model for adding item to cart"""
    pass

class CartItemUpdate(BaseModel):
    """Model for updating cart item"""
    quantity: int = Field(..., ge=1, le=99)

class CartItemResponse(CartItemBase):
    """Model for cart item response"""
    id: int
    cart_id: int
    added_at: datetime
    
    # Related data
    product: ProductResponse
    variant: Optional[ProductVariantResponse] = None
    
    class Config:
        orm_mode = True

class CartBase(BaseModel):
    """Base cart model"""
    session_id: Optional[str] = None

class CartResponse(CartBase):
    """Model for cart response"""
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    items: List[CartItemResponse] = Field(default_factory=list)
    
    # Calculated fields
    item_count: int = 0
    subtotal: float = 0.0
    
    class Config:
        orm_mode = True

class AddressBase(BaseModel):
    """Base address model"""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    company: Optional[str] = Field(None, max_length=100)
    address_line_1: str = Field(..., max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field("United States", max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

class AddressCreate(AddressBase):
    """Model for creating an address"""
    is_default_shipping: bool = False
    is_default_billing: bool = False

class AddressUpdate(BaseModel):
    """Model for updating an address"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=100)
    address_line_1: Optional[str] = Field(None, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_default_shipping: Optional[bool] = None
    is_default_billing: Optional[bool] = None

class AddressResponse(AddressBase):
    """Model for address response"""
    id: int
    user_id: int
    is_default_shipping: bool
    is_default_billing: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class OrderItemBase(BaseModel):
    """Base order item model"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., gt=0)

class OrderItemResponse(OrderItemBase):
    """Model for order item response"""
    id: int
    order_id: int
    product_name: str
    product_sku: Optional[str] = None
    variant_details: Optional[str] = None
    total_price: float
    
    # Related data
    product: Optional[ProductResponse] = None
    variant: Optional[ProductVariantResponse] = None
    
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    """Base order model"""
    shipping_address: dict
    billing_address: dict
    payment_method: str = Field(..., max_length=50)
    customer_notes: Optional[str] = None

class OrderCreate(OrderBase):
    """Model for creating an order"""
    pass

class OrderUpdate(BaseModel):
    """Model for updating an order"""
    status: Optional[str] = Field(None, regex=r'^(pending|confirmed|shipped|delivered|cancelled)$')
    payment_status: Optional[str] = Field(None, regex=r'^(pending|paid|failed|refunded)$')
    tracking_number: Optional[str] = None
    admin_notes: Optional[str] = None

class OrderResponse(OrderBase):
    """Model for order response"""
    id: int
    user_id: int
    order_number: str
    status: str
    payment_status: str
    
    # Pricing
    subtotal: float
    tax_amount: float
    shipping_amount: float
    discount_amount: float
    total_amount: float
    
    # Shipping
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    # Related data
    items: List[OrderItemResponse] = Field(default_factory=list)
    
    class Config:
        orm_mode = True

class OrderListResponse(BaseModel):
    """Model for order list response with pagination"""
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int
    pages: int