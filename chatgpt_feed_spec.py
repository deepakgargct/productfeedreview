"""
ChatGPT Product Feed Specification Schema and Validator

This module provides schema definitions and validators for product feeds
compatible with ChatGPT's product feed specification.

Complete specification with required and optional fields:
- Required: enable_search, enable_checkout, id, title, description, price, 
  currency, availability, image_link, link
- Optional: category, brand, condition, sku, gtin, shipping, sale_price, 
  rating, reviews_count, geo_price, geo_availability
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
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
    # Add more currency codes
    CHF = "CHF"
    NZD = "NZD"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"


class ProductAvailability(Enum):
    """Product availability status"""
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    PREORDER = "preorder"
    DISCONTINUED = "discontinued"


class ProductCondition(Enum):
    """Product condition"""
    NEW = "new"
    REFURBISHED = "refurbished"
    USED = "used"


@dataclass
class FieldSpec:
    """Specification for a feed field"""
    name: str
    field_type: str  # 'string', 'boolean', 'number', 'url', 'enum'
    required: bool
    description: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    default_value: Optional[Any] = None
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "field_type": self.field_type,
            "required": self.required,
            "description": self.description,
            "constraints": self.constraints,
            "default_value": self.default_value,
            "dependencies": self.dependencies
        }


@dataclass
class Price:
    """Product price specification"""
    amount: float
    currency: Union[CurrencyCode, str]
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Price amount cannot be negative")
        if isinstance(self.currency, str):
            try:
                self.currency = CurrencyCode(self.currency)
            except ValueError:
                raise ValueError(f"Invalid currency code: {self.currency}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "currency": self.currency.value if isinstance(self.currency, CurrencyCode) else self.currency
        }


@dataclass
class Shipping:
    """Shipping information"""
    cost: Optional[Price] = None
    country: Optional[str] = None
    region: Optional[str] = None
    service: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.cost:
            result["cost"] = self.cost.to_dict()
        if self.country:
            result["country"] = self.country
        if self.region:
            result["region"] = self.region
        if self.service:
            result["service"] = self.service
        return result


@dataclass
class GeoPrice:
    """Geographic-specific pricing"""
    country: str
    price: Price
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "price": self.price.to_dict()
        }


@dataclass
class GeoAvailability:
    """Geographic-specific availability"""
    country: str
    availability: ProductAvailability
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "availability": self.availability.value
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
    """
    ChatGPT Product Feed Specification
    
    Required fields:
    - enable_search: Boolean to enable search functionality
    - enable_checkout: Boolean to enable checkout (requires enable_search=True)
    - id: Unique product identifier
    - title: Product title
    - description: Product description
    - price: Product price
    - currency: Currency code
    - availability: Stock availability
    - image_link: Primary product image URL
    - link: Product page URL
    
    Optional fields:
    - category: Product category
    - brand: Product brand
    - condition: Product condition (new, refurbished, used)
    - sku: Stock keeping unit
    - gtin: Global trade item number
    - shipping: Shipping information
    - sale_price: Sale/discounted price
    - rating: Product rating (0-5)
    - reviews_count: Number of reviews
    - geo_price: Geographic-specific pricing
    - geo_availability: Geographic-specific availability
    """
    # Required fields per ChatGPT specification
    enable_search: bool
    enable_checkout: bool
    id: str
    title: str
    description: str
    price: float
    currency: Union[CurrencyCode, str]
    availability: Union[ProductAvailability, str]
    image_link: str
    link: str
    
    # Optional fields per ChatGPT specification
    category: Optional[str] = None
    brand: Optional[str] = None
    condition: Union[ProductCondition, str] = ProductCondition.NEW
    sku: Optional[str] = None
    gtin: Optional[str] = None
    shipping: Optional[Shipping] = None
    sale_price: Optional[float] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    geo_price: Optional[List[GeoPrice]] = None
    geo_availability: Optional[List[GeoAvailability]] = None
    
    # Legacy fields for backward compatibility
    url: Optional[str] = None
    images: Optional[List[Image]] = None
    review_count: Optional[int] = None
    shipping_weight: Optional[float] = None
    shipping_cost: Optional[Price] = None
    quantity_available: Optional[int] = None
    
    def __post_init__(self):
        """Validate product data and enforce dependency rules"""
        # Validate required fields
        if not self.id or not str(self.id).strip():
            raise ValueError("Product ID cannot be empty")
        if not self.title or not self.title.strip():
            raise ValueError("Product title cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Product description cannot be empty")
        
        # Validate dependency rules
        if self.enable_checkout and not self.enable_search:
            raise ValueError("enable_checkout requires enable_search to be True")
        
        # Validate URLs
        if not self.image_link.startswith(('http://', 'https://')):
            raise ValueError("image_link must be a valid HTTP(S) URL")
        if not self.link.startswith(('http://', 'https://')):
            raise ValueError("link must be a valid HTTP(S) URL")
        
        # Backward compatibility: set url if not provided
        if self.url is None:
            self.url = self.link
        
        # Validate price
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        
        # Validate sale_price if provided
        if self.sale_price is not None:
            if self.sale_price < 0:
                raise ValueError("Sale price cannot be negative")
            if self.sale_price > self.price:
                raise ValueError("Sale price cannot be greater than regular price")
        
        # Validate rating
        if self.rating is not None and not (0 <= self.rating <= 5):
            raise ValueError("Rating must be between 0 and 5")
        
        # Validate reviews_count
        if self.reviews_count is not None and self.reviews_count < 0:
            raise ValueError("Reviews count cannot be negative")
        
        # Backward compatibility for review_count
        if self.review_count is None and self.reviews_count is not None:
            self.review_count = self.reviews_count
        
        # Validate quantity_available
        if self.quantity_available is not None and self.quantity_available < 0:
            raise ValueError("Quantity available cannot be negative")
        
        # Convert string enums to enum types
        if isinstance(self.currency, str):
            try:
                self.currency = CurrencyCode(self.currency)
            except ValueError:
                pass  # Allow custom currency codes
        
        if isinstance(self.availability, str):
            try:
                self.availability = ProductAvailability(self.availability)
            except ValueError:
                raise ValueError(f"Invalid availability value: {self.availability}")
        
        if isinstance(self.condition, str):
            try:
                self.condition = ProductCondition(self.condition)
            except ValueError:
                raise ValueError(f"Invalid condition value: {self.condition}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary representation"""
        result = {
            # Required fields
            "enable_search": self.enable_search,
            "enable_checkout": self.enable_checkout,
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "currency": self.currency.value if isinstance(self.currency, CurrencyCode) else self.currency,
            "availability": self.availability.value if isinstance(self.availability, ProductAvailability) else self.availability,
            "image_link": self.image_link,
            "link": self.link,
        }
        
        # Optional fields
        if self.category:
            result["category"] = self.category
        if self.brand:
            result["brand"] = self.brand
        if self.condition:
            result["condition"] = self.condition.value if isinstance(self.condition, ProductCondition) else self.condition
        if self.sku:
            result["sku"] = self.sku
        if self.gtin:
            result["gtin"] = self.gtin
        if self.shipping:
            result["shipping"] = self.shipping.to_dict()
        if self.sale_price is not None:
            result["sale_price"] = self.sale_price
        if self.rating is not None:
            result["rating"] = self.rating
        if self.reviews_count is not None:
            result["reviews_count"] = self.reviews_count
        if self.geo_price:
            result["geo_price"] = [gp.to_dict() for gp in self.geo_price]
        if self.geo_availability:
            result["geo_availability"] = [ga.to_dict() for ga in self.geo_availability]
        
        # Legacy fields for backward compatibility
        if self.images:
            result["images"] = [img.to_dict() for img in self.images]
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


class ChatGPTFieldSpecification:
    """
    Complete ChatGPT Product Feed Field Specifications
    
    Defines all required and optional fields with their types, constraints,
    and validation rules according to ChatGPT product feed specification.
    """
    
    @staticmethod
    def get_field_specs() -> Dict[str, FieldSpec]:
        """Get all field specifications for ChatGPT product feed"""
        return {
            # Required fields
            "enable_search": FieldSpec(
                name="enable_search",
                field_type="boolean",
                required=True,
                description="Enable search functionality for this product",
                constraints={"type": "bool"},
                default_value=True
            ),
            "enable_checkout": FieldSpec(
                name="enable_checkout",
                field_type="boolean",
                required=True,
                description="Enable checkout functionality (requires enable_search=True)",
                constraints={"type": "bool"},
                dependencies=["enable_search"],
                default_value=False
            ),
            "id": FieldSpec(
                name="id",
                field_type="string",
                required=True,
                description="Unique product identifier",
                constraints={
                    "not_empty": True,
                    "max_length": 255,
                    "pattern": r"^[a-zA-Z0-9_-]+$"
                }
            ),
            "title": FieldSpec(
                name="title",
                field_type="string",
                required=True,
                description="Product title",
                constraints={
                    "not_empty": True,
                    "min_length": 1,
                    "max_length": 150
                }
            ),
            "description": FieldSpec(
                name="description",
                field_type="string",
                required=True,
                description="Product description",
                constraints={
                    "not_empty": True,
                    "min_length": 10,
                    "max_length": 5000
                }
            ),
            "price": FieldSpec(
                name="price",
                field_type="number",
                required=True,
                description="Product price",
                constraints={
                    "min": 0,
                    "type": "float"
                }
            ),
            "currency": FieldSpec(
                name="currency",
                field_type="string",
                required=True,
                description="ISO 4217 currency code",
                constraints={
                    "pattern": r"^[A-Z]{3}$",
                    "enum": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "INR", "CNY"]
                }
            ),
            "availability": FieldSpec(
                name="availability",
                field_type="enum",
                required=True,
                description="Product availability status",
                constraints={
                    "enum": ["in_stock", "out_of_stock", "preorder", "discontinued"]
                }
            ),
            "image_link": FieldSpec(
                name="image_link",
                field_type="url",
                required=True,
                description="Primary product image URL",
                constraints={
                    "pattern": r"^https?://.*\.(jpg|jpeg|png|gif|webp)$",
                    "max_length": 2000
                }
            ),
            "link": FieldSpec(
                name="link",
                field_type="url",
                required=True,
                description="Product page URL",
                constraints={
                    "pattern": r"^https?://.*",
                    "max_length": 2000
                }
            ),
            
            # Optional fields
            "category": FieldSpec(
                name="category",
                field_type="string",
                required=False,
                description="Product category",
                constraints={
                    "max_length": 255
                }
            ),
            "brand": FieldSpec(
                name="brand",
                field_type="string",
                required=False,
                description="Product brand",
                constraints={
                    "max_length": 100
                }
            ),
            "condition": FieldSpec(
                name="condition",
                field_type="enum",
                required=False,
                description="Product condition",
                constraints={
                    "enum": ["new", "refurbished", "used"]
                },
                default_value="new"
            ),
            "sku": FieldSpec(
                name="sku",
                field_type="string",
                required=False,
                description="Stock keeping unit",
                constraints={
                    "max_length": 100
                }
            ),
            "gtin": FieldSpec(
                name="gtin",
                field_type="string",
                required=False,
                description="Global trade item number (UPC, EAN, ISBN)",
                constraints={
                    "pattern": r"^\d{8,14}$"
                }
            ),
            "shipping": FieldSpec(
                name="shipping",
                field_type="object",
                required=False,
                description="Shipping information",
                constraints={
                    "type": "object",
                    "properties": ["cost", "country", "region", "service"]
                }
            ),
            "sale_price": FieldSpec(
                name="sale_price",
                field_type="number",
                required=False,
                description="Sale/discounted price",
                constraints={
                    "min": 0,
                    "type": "float"
                }
            ),
            "rating": FieldSpec(
                name="rating",
                field_type="number",
                required=False,
                description="Product rating (0-5 scale)",
                constraints={
                    "min": 0,
                    "max": 5,
                    "type": "float"
                }
            ),
            "reviews_count": FieldSpec(
                name="reviews_count",
                field_type="number",
                required=False,
                description="Number of product reviews",
                constraints={
                    "min": 0,
                    "type": "integer"
                }
            ),
            "geo_price": FieldSpec(
                name="geo_price",
                field_type="array",
                required=False,
                description="Geographic-specific pricing",
                constraints={
                    "type": "array",
                    "items": "GeoPrice"
                }
            ),
            "geo_availability": FieldSpec(
                name="geo_availability",
                field_type="array",
                required=False,
                description="Geographic-specific availability",
                constraints={
                    "type": "array",
                    "items": "GeoAvailability"
                }
            )
        }
    
    @staticmethod
    def get_required_fields() -> List[str]:
        """Get list of required field names"""
        specs = ChatGPTFieldSpecification.get_field_specs()
        return [name for name, spec in specs.items() if spec.required]
    
    @staticmethod
    def get_optional_fields() -> List[str]:
        """Get list of optional field names"""
        specs = ChatGPTFieldSpecification.get_field_specs()
        return [name for name, spec in specs.items() if not spec.required]
    
    @staticmethod
    def get_field_dependencies() -> Dict[str, List[str]]:
        """Get field dependency mapping"""
        specs = ChatGPTFieldSpecification.get_field_specs()
        return {
            name: spec.dependencies 
            for name, spec in specs.items() 
            if spec.dependencies
        }
    
    @staticmethod
    def to_json_schema() -> Dict[str, Any]:
        """Export field specifications as JSON schema"""
        specs = ChatGPTFieldSpecification.get_field_specs()
        properties = {}
        required = []
        
        for name, spec in specs.items():
            prop = {
                "description": spec.description,
                "type": spec.field_type
            }
            
            if spec.constraints:
                prop.update(spec.constraints)
            
            if spec.default_value is not None:
                prop["default"] = spec.default_value
            
            properties[name] = prop
            
            if spec.required:
                required.append(name)
        
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ChatGPT Product Feed Schema",
            "type": "object",
            "properties": properties,
            "required": required
        }


# Example usage and helper functions
def create_sample_feed() -> ProductFeed:
    """Create a sample product feed for testing"""
    
    product1 = Product(
        # Required fields
        enable_search=True,
        enable_checkout=True,
        id="PROD001",
        title="Sample Product 1",
        description="This is a sample product description with sufficient detail for ChatGPT product feed.",
        price=99.99,
        currency=CurrencyCode.USD,
        availability=ProductAvailability.IN_STOCK,
        image_link="https://example.com/product1-image1.jpg",
        link="https://example.com/products/sample-product-1",
        # Optional fields
        category="Electronics",
        brand="Example Brand",
        condition=ProductCondition.NEW,
        sku="SKU001",
        gtin="123456789012",
        rating=4.5,
        reviews_count=150,
        quantity_available=100
    )
    
    product2 = Product(
        # Required fields
        enable_search=True,
        enable_checkout=False,
        id="PROD002",
        title="Sample Product 2",
        description="Another sample product with detailed description for ChatGPT product feed specification.",
        price=149.99,
        currency="USD",
        availability="preorder",
        image_link="https://example.com/product2.jpg",
        link="https://example.com/products/sample-product-2",
        # Optional fields
        category="Electronics",
        brand="Example Brand",
        sku="SKU002",
        gtin="234567890123",
        rating=4.0,
        reviews_count=75
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
