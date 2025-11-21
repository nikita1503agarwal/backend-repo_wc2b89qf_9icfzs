"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Document QC schema
class DocumentQC(BaseModel):
    """
    Document quality check results
    Collection name: "documentqc"
    """
    document_id: str = Field(..., description="Unique identifier of the document")
    filename: Optional[str] = Field(None, description="Original file name")
    sections_expected: Optional[List[str]] = Field(default_factory=list, description="Sections that should be present")
    sections_found: Optional[List[str]] = Field(default_factory=list, description="Sections detected in the document")
    missing_sections: Optional[List[str]] = Field(default_factory=list, description="Detected missing sections")
    is_complete: Optional[bool] = Field(None, description="Whether all required sections are present")
    qc_score: Optional[float] = Field(None, ge=0, le=100, description="Optional score from 0-100")
    notes: Optional[str] = Field(None, description="Additional notes or comments")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
