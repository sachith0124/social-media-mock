from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class UserDBSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class PostSchema(BaseModel):
    title: str
    content: str
    published: bool = True

    class Config:
        from_attributes = True

class PostDBSchema(PostSchema):
    id: int
    owner_id: int
    created_at: datetime
    owner: UserDBSchema

class PostResponseSchema(PostSchema):
    id: int
    created_at: datetime
    votes: int
    owner_id: int
    owner_username: str
    owner_email: EmailStr

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str]