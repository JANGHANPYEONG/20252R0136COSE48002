"""
사용자 관련 Pydantic 스키마
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    name: str
    company: Optional[str] = None
    jobTitle: Optional[str] = None
    homeAddr: Optional[str] = None
    alarm: bool = False
    type: int

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    userId: EmailStr

class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    name: Optional[str] = None
    company: Optional[str] = None
    jobTitle: Optional[str] = None
    homeAddr: Optional[str] = None
    alarm: Optional[bool] = None
    type: Optional[int] = None

class UserResponse(UserBase):
    """사용자 응답 스키마"""
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    loginAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """사용자 로그인 스키마"""
    userId: EmailStr

class UserLoginResponse(BaseModel):
    """사용자 로그인 응답 스키마"""
    userId: str
    name: str
    homeAddr: Optional[str] = None
    company: Optional[str] = None
    jobTitle: Optional[str] = None
    type: str
    alarm: bool
    createdAt: datetime
    msg: str
