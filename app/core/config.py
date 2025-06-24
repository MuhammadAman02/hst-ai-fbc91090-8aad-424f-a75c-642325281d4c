"""
Configuration settings for ZARA E-commerce Store
Handles environment variables, database settings, and application configuration
"""

import os
from typing import Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    app_name: str = "ZARA Fashion Store"
    app_version: str = "1.0.0"
    app_description: str = "Premium fashion e-commerce platform"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    
    # Security
    secret_key: str = "zara-fashion-store-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Database
    database_url: str = "sqlite:///./zara_store.db"
    database_echo: bool = False
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    # Email Configuration (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Payment Configuration (for future integration)
    stripe_publishable_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    
    # Image Service Configuration
    unsplash_access_key: Optional[str] = None
    image_cache_duration: int = 3600  # 1 hour
    
    # Business Configuration
    default_currency: str = "USD"
    tax_rate: float = 0.08  # 8%
    free_shipping_threshold: float = 50.0
    shipping_cost: float = 5.99
    
    # Admin Configuration
    admin_username: str = "admin"
    admin_email: str = "admin@zara-store.com"
    admin_password: str = "admin123"  # Change in production!
    
    @validator('debug', pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v
    
    @validator('upload_dir')
    def create_upload_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    database_echo: bool = True

class ProductionSettings(Settings):
    """Production environment settings"""
    debug: bool = False
    database_echo: bool = False
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v == "zara-fashion-store-secret-key-change-in-production":
            raise ValueError("Secret key must be changed in production!")
        return v

class TestingSettings(Settings):
    """Testing environment settings"""
    database_url: str = "sqlite:///./test_zara_store.db"
    debug: bool = True

def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Use environment-specific settings
settings = get_settings()