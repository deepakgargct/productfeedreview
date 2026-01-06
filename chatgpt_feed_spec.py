"""
ChatGPT Product Feed Specification Schema and Validator

This module provides schema definitions and validators for product feeds
compatible with ChatGPT's product feed specification.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import json
from datetime import datetime


class FeedFormat(Enum):
    """Supported feed formats"""
    CSV = "csv"
    JSON = "json"
    XML = "xml"


class CurrencyCode(Enum):
    """ISO 4217 Currency Codes (common examples)"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    INR = "INR"
    CNY = "CNY"


class ProductAvailability(Enum):
    """Product availability status"""
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    PREORDER = "preorder"
    DISCONTINUED = "discontinued"


@dataclass
class Price:
    """Product price specification"""
    amount: float
    currency: CurrencyCode
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Price amount cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "currency": self.currency.value
        }


@dataclass
class Image:
    """Product image specification"""
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    
    def __post_init__(self):
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("Image URL must be a valid HTTP(S) URL")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "alt_text": self.alt_text,
            "is_primary": self.is_primary
        }


@dataclass
class Product:
    """Product specification"""
    id: str
    title: str
    description: str
    price: Price
    availability: ProductAvailability
    url: str
    category: str
    brand: str
    sku: Optional[str] = None
    gtin: Optional[str] = None
    images: Optional[List[Image]] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    condition: str = "new"
    shipping_weight: Optional[float] = None
    shipping_cost: Optional[Price] = None
    quantity_available: Optional[int] = None
    
    def __post_init__(self):
        """Validate product data"""
        if not self.id or not self.id.strip():
            raise ValueError("Product ID cannot be empty")
        if not self.title or not self.title.strip():
            raise ValueError("Product title cannot be empty")
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("Product URL must be a valid HTTP(S) URL")
        if self.rating is not None and not (0 <= self.rating <= 5):
            raise ValueError("Rating must be between 0 and 5")
        if self.review_count is not None and self.review_count < 0:
            raise ValueError("Review count cannot be negative")
        if self.quantity_available is not None and self.quantity_available < 0:
            raise ValueError("Quantity available cannot be negative")
        if self.condition not in ["new", "refurbished", "used"]:
            raise ValueError("Condition must be 'new', 'refurbished', or 'used'")
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price.to_dict(),
            "availability": self.availability.value,
            "url": self.url,
            "category": self.category,
            "brand": self.brand,
            "condition": self.condition,
        }
        
        if self.sku:
            result["sku"] = self.sku
        if self.gtin:
            result["gtin"] = self.gtin
        if self.images:
            result["images"] = [img.to_dict() for img in self.images]
        if self.rating is not None:
            result["rating"] = self.rating
        if self.review_count is not None:
            result["review_count"] = self.review_count
        if self.shipping_weight is not None:
            result["shipping_weight"] = self.shipping_weight
        if self.shipping_cost:
            result["shipping_cost"] = self.shipping_cost.to_dict()
        if self.quantity_available is not None:
            result["quantity_available"] = self.quantity_available
        
        return result


@dataclass
class ProductFeed:
    """Product feed specification"""
    feed_id: str
    name: str
    format: FeedFormat
    currency: CurrencyCode
    products: List[Product]
    language: str = "en"
    country: str = "US"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: str = "1.0"
    
    def __post_init__(self):
        """Validate feed data"""
        if not self.feed_id or not self.feed_id.strip():
            raise ValueError("Feed ID cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Feed name cannot be empty")
        if not self.products:
            raise ValueError("Feed must contain at least one product")
        if len(self.language) != 2:
            raise ValueError("Language code must be 2 characters (ISO 639-1)")
        if len(self.country) != 2:
            raise ValueError("Country code must be 2 characters (ISO 3166-1)")
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "feed_id": self.feed_id,
            "name": self.name,
            "format": self.format.value,
            "currency": self.currency.value,
            "language": self.language,
            "country": self.country,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
            "products": [p.to_dict() for p in self.products]
        }
    
    def to_json(self) -> str:
        """Export feed as JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class FeedValidator:
    """Validator for product feeds"""
    
    @staticmethod
    def validate_product(product: Product) -> Dict[str, Any]:
        """
        Validate a single product
        
        Args:
            product: Product instance to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        try:
            # Validation is performed in __post_init__
            product_dict = product.to_dict()
            is_valid = True
        except ValueError as e:
            errors.append(str(e))
            is_valid = False
        
        # Additional warnings
        if not product.images:
            warnings.append("Product has no images")
        if product.rating is None:
            warnings.append("Product has no rating")
        if product.review_count is None:
            warnings.append("Product has no review count")
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_feed(feed: ProductFeed) -> Dict[str, Any]:
        """
        Validate an entire feed
        
        Args:
            feed: ProductFeed instance to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        try:
            feed_dict = feed.to_dict()
            is_valid = True
        except ValueError as e:
            errors.append(f"Feed validation error: {str(e)}")
            is_valid = False
            return {
                "is_valid": is_valid,
                "errors": errors,
                "warnings": warnings,
                "product_validations": []
            }
        
        # Validate each product
        product_validations = []
        for i, product in enumerate(feed.products):
            validation = FeedValidator.validate_product(product)
            validation["product_id"] = product.id
            validation["product_index"] = i
            product_validations.append(validation)
            
            if not validation["is_valid"]:
                errors.append(f"Product {i} ({product.id}) is invalid")
            if validation["warnings"]:
                warnings.extend([f"Product {i}: {w}" for w in validation["warnings"]])
        
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "product_count": len(feed.products),
            "product_validations": product_validations
        }


# Example usage and helper functions
def create_sample_feed() -> ProductFeed:
    """Create a sample product feed for testing"""
    price = Price(amount=99.99, currency=CurrencyCode.USD)
    shipping_price = Price(amount=5.99, currency=CurrencyCode.USD)
    
    image1 = Image(
        url="https://example.com/product1-image1.jpg",
        alt_text="Product front view",
        is_primary=True
    )
    image2 = Image(
        url="https://example.com/product1-image2.jpg",
        alt_text="Product back view",
        is_primary=False
    )
    
    product1 = Product(
        id="PROD001",
        title="Sample Product 1",
        description="This is a sample product description",
        price=price,
        availability=ProductAvailability.IN_STOCK,
        url="https://example.com/products/sample-product-1",
        category="Electronics",
        brand="Example Brand",
        sku="SKU001",
        gtin="123456789012",
        images=[image1, image2],
        rating=4.5,
        review_count=150,
        condition="new",
        quantity_available=100,
        shipping_cost=shipping_price
    )
    
    product2 = Product(
        id="PROD002",
        title="Sample Product 2",
        description="Another sample product",
        price=Price(amount=149.99, currency=CurrencyCode.USD),
        availability=ProductAvailability.PREORDER,
        url="https://example.com/products/sample-product-2",
        category="Electronics",
        brand="Example Brand",
        sku="SKU002",
        gtin="234567890123",
        images=[Image(url="https://example.com/product2.jpg", is_primary=True)],
        rating=4.0,
        review_count=75
    )
    
    feed = ProductFeed(
        feed_id="FEED001",
        name="Sample Product Feed",
        format=FeedFormat.JSON,
        currency=CurrencyCode.USD,
        products=[product1, product2],
        language="en",
        country="US"
    )
    
    return feed


if __name__ == "__main__":
    # Example usage
    feed = create_sample_feed()
    
    # Validate feed
    validator = FeedValidator()
    validation_result = validator.validate_feed(feed)
    
    print("Feed Validation Results:")
    print(json.dumps(validation_result, indent=2, default=str))
    
    print("\n" + "="*50)
    print("Feed JSON Export:")
    print(feed.to_json())
