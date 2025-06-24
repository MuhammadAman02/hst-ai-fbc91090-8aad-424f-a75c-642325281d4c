"""
Product-related Pydantic models for API serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    """Base category model"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    """Model for creating a category"""
    pass

class CategoryResponse(CategoryBase):
    """Model for category response"""
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductVariantBase(BaseModel):
    """Base product variant model"""
    size: Optional[str] = None
    color: Optional[str] = None
    color_code: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    material: Optional[str] = None
    sku: Optional[str] = None
    price_adjustment: float = 0.0
    stock_quantity: int = 0
    image_url: Optional[str] = None
    is_active: bool = True

class ProductVariantCreate(ProductVariantBase):
    """Model for creating a product variant"""
    pass

class ProductVariantResponse(ProductVariantBase):
    """Model for product variant response"""
    id: int
    product_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductImageBase(BaseModel):
    """Base product image model"""
    image_url: str = Field(..., max_length=500)
    alt_text: Optional[str] = Field(None, max_length=200)
    sort_order: int = 0
    is_primary: bool = False

class ProductImageCreate(ProductImageBase):
    """Model for creating a product image"""
    pass

class ProductImageResponse(ProductImageBase):
    """Model for product image response"""
    id: int
    product_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    """Base product model"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = Field(None, max_length=100)
    stock_quantity: int = Field(0, ge=0)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_featured: bool = False
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    image_alt: Optional[str] = Field(None, max_length=200)

class ProductCreate(ProductBase):
    """Model for creating a product"""
    category_ids: List[int] = Field(default_factory=list)
    
    @validator('price', 'compare_at_price')
    def validate_prices(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

class ProductUpdate(BaseModel):
    """Model for updating a product"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    category_ids: Optional[List[int]] = None

class ProductResponse(ProductBase):
    """Model for product response"""
    id: int
    slug: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    categories: List[CategoryResponse] = Field(default_factory=list)
    variants: List[ProductVariantResponse] = Field(default_factory=list)
    images: List[ProductImageResponse] = Field(default_factory=list)
    
    class Config:
        orm_mode = True

class ProductListResponse(BaseModel):
    """Model for product list response with pagination"""
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int
    pages: int

class ProductSearchRequest(BaseModel):
    """Model for product search request"""
    query: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    in_stock_only: bool = True
    is_featured: Optional[bool] = None
    sort_by: str = Field("created_at", regex=r'^(name|price|created_at|updated_at)$')
    sort_order: str = Field("desc", regex=r'^(asc|desc)$')
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)