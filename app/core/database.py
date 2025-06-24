"""
Database configuration and models for ZARA E-commerce Store
SQLAlchemy setup with async support and comprehensive e-commerce models
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
import asyncio
from contextlib import asynccontextmanager

from app.core.config import settings

# Database setup
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables for many-to-many relationships
product_categories = Table(
    'product_categories',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

order_products = Table(
    'order_products',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('quantity', Integer, default=1),
    Column('price_at_time', Float)
)

class User(Base):
    """User model for customer accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)
    reviews = relationship("Review", back_populates="user")

class Category(Base):
    """Product category model"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    parent_id = Column(Integer, ForeignKey('categories.id'))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Self-referential relationship for subcategories
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category")
    
    # Many-to-many with products
    products = relationship("Product", secondary=product_categories, back_populates="categories")

class Product(Base):
    """Product model for fashion items"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float)  # Original price for sale items
    sku = Column(String(100), unique=True, index=True)
    barcode = Column(String(100))
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=5)
    weight = Column(Float)  # in grams
    dimensions = Column(String(100))  # LxWxH in cm
    
    # Product status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_digital = Column(Boolean, default=False)
    
    # SEO and metadata
    meta_title = Column(String(200))
    meta_description = Column(Text)
    slug = Column(String(200), unique=True, index=True)
    
    # Images
    image_url = Column(String(500))
    image_alt = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    categories = relationship("Category", secondary=product_categories, back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

class ProductVariant(Base):
    """Product variants for size, color, etc."""
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # Variant attributes
    size = Column(String(20))
    color = Column(String(50))
    color_code = Column(String(7))  # Hex color code
    material = Column(String(100))
    
    # Variant-specific details
    sku = Column(String(100), unique=True)
    price_adjustment = Column(Float, default=0.0)
    stock_quantity = Column(Integer, default=0)
    weight_adjustment = Column(Float, default=0.0)
    
    # Images specific to this variant
    image_url = Column(String(500))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="variants")

class ProductImage(Base):
    """Additional product images"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(200))
    sort_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")

class Cart(Base):
    """Shopping cart model"""
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(100))  # For guest carts
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    """Cart item model"""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id'))
    
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("ProductVariant")

class Address(Base):
    """User address model"""
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Address fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(100))
    address_line_1 = Column(String(200), nullable=False)
    address_line_2 = Column(String(200))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="United States")
    phone = Column(String(20))
    
    # Address type and status
    is_default_shipping = Column(Boolean, default=False)
    is_default_billing = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="addresses")

class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    
    # Order status
    status = Column(String(50), default="pending")  # pending, confirmed, shipped, delivered, cancelled
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Addresses (stored as JSON or separate fields)
    shipping_address = Column(Text)  # JSON string
    billing_address = Column(Text)   # JSON string
    
    # Payment information
    payment_method = Column(String(50))
    payment_reference = Column(String(200))
    
    # Shipping information
    shipping_method = Column(String(100))
    tracking_number = Column(String(100))
    
    # Notes
    customer_notes = Column(Text)
    admin_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    """Order item model"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id'))
    
    # Item details at time of order
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100))
    variant_details = Column(String(200))  # Size, color, etc.
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")

class Review(Base):
    """Product review model"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200))
    comment = Column(Text)
    
    # Review status
    is_approved = Column(Boolean, default=False)
    is_verified_purchase = Column(Boolean, default=False)
    
    # Helpful votes
    helpful_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

# Database session management
@asynccontextmanager
async def get_session():
    """Get database session with proper cleanup"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user and sample data
    await create_default_data()

async def create_default_data():
    """Create default admin user and sample categories"""
    from app.services.auth_service import AuthService
    from app.core.assets import FashionAssetManager
    
    auth_service = AuthService()
    asset_manager = FashionAssetManager()
    
    async with get_session() as session:
        # Check if admin user exists
        admin_user = session.query(User).filter(User.username == settings.admin_username).first()
        if not admin_user:
            # Create admin user
            admin_user = await auth_service.create_user(
                username=settings.admin_username,
                email=settings.admin_email,
                password=settings.admin_password,
                full_name="Store Administrator",
                is_admin=True
            )
        
        # Create default categories
        default_categories = [
            {"name": "Women", "description": "Women's fashion and accessories"},
            {"name": "Men", "description": "Men's fashion and accessories"},
            {"name": "Kids", "description": "Children's clothing and accessories"},
            {"name": "Accessories", "description": "Fashion accessories for all"},
            {"name": "Sale", "description": "Discounted items"},
        ]
        
        for cat_data in default_categories:
            existing_cat = session.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing_cat:
                category = Category(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    image_url=asset_manager.get_category_image(cat_data["name"].lower())
                )
                session.add(category)
        
        session.commit()