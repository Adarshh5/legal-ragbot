from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import uuid


class UserCreateModel(BaseModel):
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str  = Field(min_length=6)



class UserLoggingModel(BaseModel):
     email: str = Field(max_length=40)
     password: str  = Field(min_length=6)

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    is_verified: bool 
    password_hash:str = Field(exclude=True)
    email: str
    created_at: datetime

class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str