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

# Example schemas (retain as reference)

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

# Lamrrari specific schemas

class Build(BaseModel):
    """
    Customer car builds (configurator)
    Collection name: "build"
    """
    model_id: str = Field(..., description="ID of the selected model")
    model_name: str = Field(..., description="Name of the selected model")
    color: str = Field(..., description="Selected exterior color (hex or name)")
    wheels: str = Field(..., description="Selected wheel design")
    interior: str = Field(..., description="Selected interior theme")
    addons: List[str] = Field(default_factory=list, description="Optional add-on packages")
    region: Optional[str] = Field(None, description="Market region (e.g., UAE, EU, IN)")
    price: float = Field(..., ge=0, description="Final configured price in USD")
    customer_name: Optional[str] = Field(None, description="Optional: customer name for lead")
    customer_email: Optional[str] = Field(None, description="Optional: customer email for lead")
