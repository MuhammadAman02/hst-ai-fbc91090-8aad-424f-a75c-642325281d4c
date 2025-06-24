"""
User-related Pydantic models for API serialization
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base user model with common attributes"""
    username: str = Field(..., min_length=3, max_length=50, description="Username for login")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of the user")
    is_active: bool = Field(True, description="Whether the user is active")

class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, description="Password for login")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    """Model for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    """Model for user information returned to clients"""
    id: int
    is_admin: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """Model for user login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class Token(BaseModel):
    """Model for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Model for data stored in JWT token"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: bool = False