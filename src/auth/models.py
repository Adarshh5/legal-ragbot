from uuid import UUID
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, VARCHAR
from sqlalchemy.sql import expression
import sqlalchemy as sa 
import uuid
from typing import Optional, List
from src.ragbot.models import UserTotalTime, UserDailyMessageUsage

class UserRole(str, Enum):
    user = "user"
    staff = "staff"
    superuser = "superuser"

class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    uid: UUID = Field(
        default_factory=uuid.uuid4,
      
        sa_column=Column(
            PG_UUID(as_uuid=True),
            server_default=text("gen_random_uuid()"),
            primary_key=True,
            unique=True,
            nullable=False
        )
    )
    
    username: str = Field(max_length=50, nullable=False)
    email: str = Field(max_length=255, nullable=False, unique=True)
    role: UserRole = Field(
        default=UserRole.user,
        sa_column=Column(VARCHAR(20), nullable=False, server_default=UserRole.user.value)
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(nullable=False)
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            sa.TIMESTAMP(timezone=True),
            server_default=func.now()
        )
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            sa.TIMESTAMP(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        )
    )

    total_time: Optional["UserTotalTime"] = Relationship(back_populates="user")
    daily_usage: List["UserDailyMessageUsage"] = Relationship(back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"

