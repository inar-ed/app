from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    age: Optional[int] = Field(None, ge=0, le=150, description="Возраст")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)


class User(UserCreate):
    id: int