
from sqlmodel import SQLModel, Field, Relationship, SQLModel
from sqlalchemy import Column, func, text
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as  VARCHAR
from datetime import datetime, date

from typing import List, Optional
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy import UniqueConstraint, DATE, ForeignKey

from sqlalchemy import UUID as SA_UUID  # Not PG_UUID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.auth.models import User
class UserTotalTime(SQLModel, table=True):
    model_config = {"arbitrary_types_allowed": True}

    __tablename__ = "user_total_time"
    
    # One-to-one relationship (like Django's OneToOneField)
    user_id: UUID = Field(
        sa_column=Column(  SA_UUID(as_uuid=True),
        ForeignKey("user_accounts.uid"),
        primary_key=True))
    
    start_date: datetime = Field(
        sa_column=Column(
            sa.TIMESTAMP(timezone=True),
            server_default=func.now()
        )
    )
    
    # For the one-to-one relationship behavior
    user: "User" = Relationship(back_populates="total_time")




class UserDailyMessageUsage(SQLModel, table=True):
    model_config = {"arbitrary_types_allowed": True}

    __tablename__ = "user_daily_message_usage"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: UUID = Field(
        
        sa_column=Column(SA_UUID(as_uuid=True), ForeignKey("user_accounts.uid")))
    
    usage_date: date = Field(  # Changed to date (not datetime)
        sa_column=Column(
            DATE(),
            server_default=func.current_date()
        )
    )
    
    message_count: int = Field(default=0)
    
    # For the many-to-one relationship
    user: "User" = Relationship(back_populates="daily_usage")
    
    # Unique constraint equivalent to Django's unique_together
    __table_args__ = (
        UniqueConstraint('user_id', 'usage_date', name='unique_user_daily_usage'),
    )