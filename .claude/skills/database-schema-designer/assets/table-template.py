"""
SQLModel Table Template

Copy this template when creating new database tables.
Fill in the sections marked with comments.
"""

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional
from pydantic import validator


class TableName(SQLModel, table=True):
    """
    [Brief description of what this table stores]

    Relationships:
    - [Describe any relationships]

    Indexes:
    - [List indexed fields and why]
    """

    __tablename__ = "table_name"  # lowercase, plural

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys (always index)
    user_id: str = Field(foreign_key="users.id", index=True)
    # Add other foreign keys here

    # Required Fields
    # Add required fields with proper validation
    # name: str = Field(max_length=100, min_length=1)

    # Optional Fields
    # Add optional fields with default values
    # description: Optional[str] = Field(default=None, max_length=500)

    # Boolean Fields (index if frequently queried)
    # active: bool = Field(default=True, index=True)

    # Timestamps (always include)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (optional, for navigation)
    # user: Optional["User"] = Relationship(back_populates="items")

    # Validators (optional, for custom validation)
    # @validator('name')
    # def name_must_not_be_empty(cls, v):
    #     if not v.strip():
    #         raise ValueError('Name cannot be empty')
    #     return v


# ============================================================================
# Usage Example
# ============================================================================

"""
# 1. Import in models.py
from models.table_name import TableName

# 2. Create database tables
from sqlmodel import create_engine
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

# 3. Use in FastAPI endpoints
from fastapi import Depends
from sqlmodel import Session

@app.post("/items/")
def create_item(item: TableName, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
"""
