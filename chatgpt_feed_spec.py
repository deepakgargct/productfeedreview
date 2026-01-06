"""
ChatGPT Product Feed Specification Module

This module defines the complete specification for ChatGPT product feeds,
including all required and optional fields with validation rules and
dependency management.

Created: 2026-01-06 14:07:31 UTC
Author: deepakgargct
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime


class FieldType(Enum):
    """Enumeration of valid field types in ChatGPT feed specification."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    URL = "url"
    EMAIL = "email"
    ENUM = "enum"
    LIST = "list"
    OBJECT = "object"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"


class ValidationRule(ABC):
    """Abstract base class for validation rules."""
    
    @abstractmethod
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against the rule.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        pass


class StringLengthRule(ValidationRule):
    """Validates string length constraints."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, "Value must be a string"
        
        if self.min_length and len(value) < self.min_length:
            return False, f"String length must be at least {self.min_length}"
        
        if self.max_length and len(value) > self.max_length:
            return False, f"String length must not exceed {self.max_length}"
        
        return True, None


class NumericRangeRule(ValidationRule):
    """Validates numeric value ranges."""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None):
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, (int, float)):
            return False, "Value must be numeric"
        
        if self.min_value is not None and value < self.min_value:
            return False, f"Value must be at least {self.min_value}"
        
        if self.max_value is not None and value > self.max_value:
            return False, f"Value must not exceed {self.max_value}"
        
        return True, None


class PatternRule(ValidationRule):
    """Validates values against regex patterns."""
    
    def __init__(self, pattern: str, description: str = ""):
        import re
        self.pattern = re.compile(pattern)
        self.description = description
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, "Value must be a string"
        
        if not self.pattern.match(value):
            error_msg = f"Value does not match pattern{': ' + self.description if self.description else ''}"
            return False, error_msg
        
        return True, None


class EnumRule(ValidationRule):
    """Validates values against allowed enumerations."""
    
    def __init__(self, allowed_values: List[str]):
        self.allowed_values = set(allowed_values)
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if value not in self.allowed_values:
            return False, f"Value must be one of {sorted(self.allowed_values)}"
        
        return True, None


class URLRule(ValidationRule):
    """Validates URL format."""
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, "Value must be a string"
        
        # Simple URL validation
        if not value.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        try:
            from urllib.parse import urlparse
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                return False, "Invalid URL format"
        except Exception:
            return False, "Invalid URL format"
        
        return True, None


class EmailRule(ValidationRule):
    """Validates email format."""
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, "Value must be a string"
        
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return False, "Invalid email format"
        
        return True, None


class CurrencyRule(ValidationRule):
    """Validates currency format (e.g., USD, EUR, GBP)."""
    
    VALID_CURRENCIES = {
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR',
        'MXN', 'BRL', 'ZAR', 'SGD', 'HKD', 'NZD', 'KRW', 'SEK', 'NOK'
    }
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, "Currency code must be a string"
        
        if value.upper() not in self.VALID_CURRENCIES:
            return False, f"Invalid currency code. Must be one of {sorted(self.VALID_CURRENCIES)}"
        
        return True, None


class DependencyRule(ABC):
    """Abstract base class for field dependencies."""
    
    @abstractmethod
    def check(self, fields: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Check if dependency is satisfied.
        
        Returns:
            tuple: (is_satisfied, error_message)
        """
        pass


class RequiredIfRule(DependencyRule):
    """Field is required if another field has a specific value."""
    
    def __init__(self, field_name: str, required_field: str, trigger_value: Any = True):
        self.field_name = field_name
        self.required_field = required_field
        self.trigger_value = trigger_value
    
    def check(self, fields: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        if fields.get(self.required_field) == self.trigger_value:
            if self.field_name not in fields or fields[self.field_name] is None:
                return False, f"Field '{self.field_name}' is required when '{self.required_field}' is {self.trigger_value}"
        
        return True, None


class MutuallyExclusiveRule(DependencyRule):
    """Fields cannot both be present."""
    
    def __init__(self, field1: str, field2: str):
        self.field1 = field1
        self.field2 = field2
    
    def check(self, fields: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        has_field1 = self.field1 in fields and fields[self.field1] is not None
        has_field2 = self.field2 in fields and fields[self.field2] is not None
        
        if has_field1 and has_field2:
            return False, f"Fields '{self.field1}' and '{self.field2}' cannot both be present"
        
        return True, None


class AtLeastOneRule(DependencyRule):
    """At least one of the specified fields must be present."""
    
    def __init__(self, fields: List[str]):
        self.fields = fields
    
    def check(self, fields: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        has_any = any(f in fields and fields[f] is not None for f in self.fields)
        
        if not has_any:
            return False, f"At least one of {self.fields} must be present"
        
        return True, None


@dataclass
class FieldDefinition:
    """
    Defines a single field in the ChatGPT feed specification.
    """
    name: str
    field_type: FieldType
    required: bool = False
    description: str = ""
    validation_rules: List[ValidationRule] = field(default_factory=list)
    default_value: Optional[Any] = None
    examples: List[Any] = field(default_factory=list)
    nested_fields: Optional[Dict[str, 'FieldDefinition']] = None
    enum_values: Optional[List[str]] = None
    max_items: Optional[int] = None  # For list types
    min_items: Optional[int] = None  # For list types
    
    def validate(self, value: Any) -> tuple[bool, List[str]]:
        """
        Validate a value against this field definition.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check type
        if value is None:
            if self.required:
                errors.append(f"Field '{self.name}' is required")
            return len(errors) == 0, errors
        
        # Validate against rules
        for rule in self.validation_rules:
            is_valid, error_msg = rule.validate(value)
            if not is_valid:
                errors.append(error_msg or f"Validation failed for field '{self.name}'")
        
        return len(errors) == 0, errors


class ChatGPTFeedSpec:
    """
    Complete ChatGPT Product Feed Specification.
    
    This class defines all required and optional fields for ChatGPT product feeds
    with comprehensive validation rules and dependency management.
    """
    
    # Core Product Fields
    PRODUCT_ID = FieldDefinition(
        name="id",
        field_type=FieldType.STRING,
        required=True,
        description="Unique identifier for the product",
        validation_rules=[StringLengthRule(min_length=1, max_length=100)],
        examples=["PROD-12345", "SKU-789", "P-ABC123"]
    )
    
    PRODUCT_TITLE = FieldDefinition(
        name="title",
        field_type=FieldType.STRING,
        required=True,
        description="Product name/title",
        validation_rules=[StringLengthRule(min_length=3, max_length=255)],
        examples=["Wireless Bluetooth Headphones", "Premium Stainless Steel Water Bottle"]
    )
    
    PRODUCT_DESCRIPTION = FieldDefinition(
        name="description",
        field_type=FieldType.STRING,
        required=False,
        description="Detailed product description",
        validation_rules=[StringLengthRule(max_length=5000)],
        examples=["High-quality wireless headphones with noise cancellation..."]
    )
    
    PRODUCT_CATEGORY = FieldDefinition(
        name="category",
        field_type=FieldType.STRING,
        required=True,
        description="Product category",
        validation_rules=[StringLengthRule(min_length=2, max_length=100)],
        examples=["Electronics", "Home & Garden", "Sports & Outdoors"]
    )
    
    PRODUCT_SKU = FieldDefinition(
        name="sku",
        field_type=FieldType.STRING,
        required=False,
        description="Stock Keeping Unit",
        validation_rules=[StringLengthRule(max_length=50)],
        examples=["SKU-12345", "PROD-ABC-789"]
    )
    
    PRODUCT_BRAND = FieldDefinition(
        name="brand",
        field_type=FieldType.STRING,
        required=False,
        description="Product brand/manufacturer",
        validation_rules=[StringLengthRule(max_length=100)],
        examples=["Sony", "Apple", "Samsung"]
    )
    
    PRODUCT_URL = FieldDefinition(
        name="product_url",
        field_type=FieldType.URL,
        required=False,
        description="Direct link to product page",
        validation_rules=[URLRule()],
        examples=["https://example.com/products/headphones"]
    )
    
    PRODUCT_IMAGE_URL = FieldDefinition(
        name="image_url",
        field_type=FieldType.URL,
        required=False,
        description="URL to product image",
        validation_rules=[URLRule()],
        examples=["https://example.com/images/product.jpg"]
    )
    
    PRODUCT_IMAGE_URLS = FieldDefinition(
        name="image_urls",
        field_type=FieldType.LIST,
        required=False,
        description="Multiple product images",
        max_items=10,
        examples=[["https://example.com/img1.jpg", "https://example.com/img2.jpg"]]
    )
    
    # Pricing Fields
    PRODUCT_PRICE = FieldDefinition(
        name="price",
        field_type=FieldType.CURRENCY,
        required=True,
        description="Product price in specified currency",
        validation_rules=[NumericRangeRule(min_value=0)],
        examples=[29.99, 99.95, 199.99]
    )
    
    PRODUCT_CURRENCY = FieldDefinition(
        name="currency",
        field_type=FieldType.STRING,
        required=True,
        description="Currency code (ISO 4217)",
        validation_rules=[CurrencyRule()],
        examples=["USD", "EUR", "GBP"]
    )
    
    PRODUCT_ORIGINAL_PRICE = FieldDefinition(
        name="original_price",
        field_type=FieldType.FLOAT,
        required=False,
        description="Original price before discount",
        validation_rules=[NumericRangeRule(min_value=0)],
        examples=[39.99, 149.99]
    )
    
    PRODUCT_DISCOUNT_PERCENTAGE = FieldDefinition(
        name="discount_percentage",
        field_type=FieldType.FLOAT,
        required=False,
        description="Discount percentage",
        validation_rules=[NumericRangeRule(min_value=0, max_value=100)],
        examples=[10, 25, 50]
    )
    
    # Availability & Inventory
    PRODUCT_AVAILABILITY = FieldDefinition(
        name="availability",
        field_type=FieldType.STRING,
        required=False,
        description="Product availability status",
        validation_rules=[EnumRule(['in_stock', 'out_of_stock', 'preorder', 'discontinued'])],
        examples=["in_stock", "out_of_stock", "preorder"]
    )
    
    PRODUCT_STOCK_QUANTITY = FieldDefinition(
        name="stock_quantity",
        field_type=FieldType.INTEGER,
        required=False,
        description="Available stock quantity",
        validation_rules=[NumericRangeRule(min_value=0)],
        examples=[100, 50, 999]
    )
    
    PRODUCT_DELIVERY_TIME = FieldDefinition(
        name="delivery_time_days",
        field_type=FieldType.INTEGER,
        required=False,
        description="Expected delivery time in days",
        validation_rules=[NumericRangeRule(min_value=0, max_value=365)],
        examples=[1, 3, 7, 14]
    )
    
    # Ratings & Reviews
    PRODUCT_RATING = FieldDefinition(
        name="rating",
        field_type=FieldType.FLOAT,
        required=False,
        description="Product rating (0-5 scale)",
        validation_rules=[NumericRangeRule(min_value=0, max_value=5)],
        examples=[4.5, 3.8, 4.9]
    )
    
    PRODUCT_REVIEW_COUNT = FieldDefinition(
        name="review_count",
        field_type=FieldType.INTEGER,
        required=False,
        description="Number of customer reviews",
        validation_rules=[NumericRangeRule(min_value=0)],
        examples=[150, 500, 1000]
    )
    
    PRODUCT_REVIEWS = FieldDefinition(
        name="reviews",
        field_type=FieldType.LIST,
        required=False,
        description="Customer review details",
        max_items=50,
        examples=[[{"rating": 5, "text": "Great product!"}, {"rating": 4, "text": "Good value"}]]
    )
    
    # Specifications & Attributes
    PRODUCT_SPECIFICATIONS = FieldDefinition(
        name="specifications",
        field_type=FieldType.OBJECT,
        required=False,
        description="Product specifications and attributes",
        examples=[{
            "weight": "500g",
            "dimensions": "10x20x30cm",
            "color": "black",
            "battery_life": "20 hours"
        }]
    )
    
    PRODUCT_COLOR = FieldDefinition(
        name="color",
        field_type=FieldType.STRING,
        required=False,
        description="Product color",
        validation_rules=[StringLengthRule(max_length=50)],
        examples=["Black", "Blue", "Red", "Silver"]
    )
    
    PRODUCT_SIZE = FieldDefinition(
        name="size",
        field_type=FieldType.STRING,
        required=False,
        description="Product size",
        validation_rules=[StringLengthRule(max_length=50)],
        examples=["S", "M", "L", "XL", "One Size"]
    )
    
    PRODUCT_WEIGHT = FieldDefinition(
        name="weight",
        field_type=FieldType.STRING,
        required=False,
        description="Product weight with unit",
        validation_rules=[StringLengthRule(max_length=50)],
        examples=["500g", "2.5kg", "1.2 lbs"]
    )
    
    PRODUCT_DIMENSIONS = FieldDefinition(
        name="dimensions",
        field_type=FieldType.STRING,
        required=False,
        description="Product dimensions (L x W x H)",
        validation_rules=[StringLengthRule(max_length=100)],
        examples=["30x20x10cm", "12x8x4 inches"]
    )
    
    PRODUCT_MATERIAL = FieldDefinition(
        name="material",
        field_type=FieldType.STRING,
        required=False,
        description="Product material composition",
        validation_rules=[StringLengthRule(max_length=255)],
        examples=["Stainless Steel", "100% Cotton", "Aluminum"]
    )
    
    # Additional Attributes
    PRODUCT_KEYWORDS = FieldDefinition(
        name="keywords",
        field_type=FieldType.LIST,
        required=False,
        description="Search keywords for the product",
        max_items=20,
        examples=[["wireless", "headphones", "noise-cancelling"]]
    )
    
    PRODUCT_TAGS = FieldDefinition(
        name="tags",
        field_type=FieldType.LIST,
        required=False,
        description="Product tags for categorization",
        max_items=20,
        examples=[["bestseller", "new", "eco-friendly"]]
    )
    
    PRODUCT_WARRANTY = FieldDefinition(
        name="warranty",
        field_type=FieldType.STRING,
        required=False,
        description="Warranty information",
        validation_rules=[StringLengthRule(max_length=500)],
        examples=["1 year manufacturer warranty", "Lifetime warranty"]
    )
    
    PRODUCT_RETURN_POLICY = FieldDefinition(
        name="return_policy",
        field_type=FieldType.STRING,
        required=False,
        description="Product return policy",
        validation_rules=[StringLengthRule(max_length=500)],
        examples=["30-day money-back guarantee", "No returns"]
    )
    
    # Seller Information
    SELLER_NAME = FieldDefinition(
        name="seller_name",
        field_type=FieldType.STRING,
        required=False,
        description="Seller/vendor name",
        validation_rules=[StringLengthRule(max_length=100)],
        examples=["Amazon", "Best Buy", "eBay Seller"]
    )
    
    SELLER_RATING = FieldDefinition(
        name="seller_rating",
        field_type=FieldType.FLOAT,
        required=False,
        description="Seller rating",
        validation_rules=[NumericRangeRule(min_value=0, max_value=5)],
        examples=[4.8, 4.5]
    )
    
    SELLER_EMAIL = FieldDefinition(
        name="seller_email",
        field_type=FieldType.EMAIL,
        required=False,
        description="Seller contact email",
        validation_rules=[EmailRule()],
        examples=["seller@example.com"]
    )
    
    # Metadata
    FEED_UPDATED_AT = FieldDefinition(
        name="updated_at",
        field_type=FieldType.DATETIME,
        required=False,
        description="Last update timestamp",
        examples=["2026-01-06T14:07:31Z"]
    )
    
    FEED_CREATED_AT = FieldDefinition(
        name="created_at",
        field_type=FieldType.DATETIME,
        required=False,
        description="Creation timestamp",
        examples=["2025-01-01T10:00:00Z"]
    )
    
    PRODUCT_ACTIVE = FieldDefinition(
        name="is_active",
        field_type=FieldType.BOOLEAN,
        required=False,
        description="Whether product is actively listed",
        default_value=True,
        examples=[True, False]
    )
    
    # Define all fields
    ALL_FIELDS: Dict[str, FieldDefinition] = {
        "id": PRODUCT_ID,
        "title": PRODUCT_TITLE,
        "description": PRODUCT_DESCRIPTION,
        "category": PRODUCT_CATEGORY,
        "sku": PRODUCT_SKU,
        "brand": PRODUCT_BRAND,
        "product_url": PRODUCT_URL,
        "image_url": PRODUCT_IMAGE_URL,
        "image_urls": PRODUCT_IMAGE_URLS,
        "price": PRODUCT_PRICE,
        "currency": PRODUCT_CURRENCY,
        "original_price": PRODUCT_ORIGINAL_PRICE,
        "discount_percentage": PRODUCT_DISCOUNT_PERCENTAGE,
        "availability": PRODUCT_AVAILABILITY,
        "stock_quantity": PRODUCT_STOCK_QUANTITY,
        "delivery_time_days": PRODUCT_DELIVERY_TIME,
        "rating": PRODUCT_RATING,
        "review_count": PRODUCT_REVIEW_COUNT,
        "reviews": PRODUCT_REVIEWS,
        "specifications": PRODUCT_SPECIFICATIONS,
        "color": PRODUCT_COLOR,
        "size": PRODUCT_SIZE,
        "weight": PRODUCT_WEIGHT,
        "dimensions": PRODUCT_DIMENSIONS,
        "material": PRODUCT_MATERIAL,
        "keywords": PRODUCT_KEYWORDS,
        "tags": PRODUCT_TAGS,
        "warranty": PRODUCT_WARRANTY,
        "return_policy": PRODUCT_RETURN_POLICY,
        "seller_name": SELLER_NAME,
        "seller_rating": SELLER_RATING,
        "seller_email": SELLER_EMAIL,
        "updated_at": FEED_UPDATED_AT,
        "created_at": FEED_CREATED_AT,
        "is_active": PRODUCT_ACTIVE,
    }
    
    # Define dependencies
    DEPENDENCIES: List[DependencyRule] = [
        RequiredIfRule("currency", "price", True),
        RequiredIfRule("discount_percentage", "original_price", True),
        MutuallyExclusiveRule("image_url", "image_urls"),
    ]
    
    @classmethod
    def get_required_fields(cls) -> List[str]:
        """Get list of required field names."""
        return [name for name, field in cls.ALL_FIELDS.items() if field.required]
    
    @classmethod
    def get_optional_fields(cls) -> List[str]:
        """Get list of optional field names."""
        return [name for name, field in cls.ALL_FIELDS.items() if not field.required]
    
    @classmethod
    def get_field_definition(cls, field_name: str) -> Optional[FieldDefinition]:
        """Get definition for a specific field."""
        return cls.ALL_FIELDS.get(field_name)
    
    @classmethod
    def validate_product(cls, product_data: Dict[str, Any]) -> tuple[bool, Dict[str, List[str]]]:
        """
        Validate a complete product record.
        
        Returns:
            tuple: (is_valid, errors_dict)
        """
        errors = {}
        
        # Validate each field
        for field_name, field_def in cls.ALL_FIELDS.items():
            value = product_data.get(field_name)
            is_valid, field_errors = field_def.validate(value)
            
            if not is_valid:
                errors[field_name] = field_errors
        
        # Validate dependencies
        for dependency in cls.DEPENDENCIES:
            is_satisfied, error_msg = dependency.check(product_data)
            if not is_satisfied:
                # Store dependency errors under a special key
                if "dependencies" not in errors:
                    errors["dependencies"] = []
                errors["dependencies"].append(error_msg)
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_spec_summary(cls) -> Dict[str, Any]:
        """Get a summary of the feed specification."""
        return {
            "total_fields": len(cls.ALL_FIELDS),
            "required_fields": cls.get_required_fields(),
            "optional_fields": cls.get_optional_fields(),
            "field_count_by_type": {
                ftype.value: sum(1 for f in cls.ALL_FIELDS.values() if f.field_type == ftype)
                for ftype in FieldType
            },
            "dependencies_count": len(cls.DEPENDENCIES),
        }


# Example usage and validation
if __name__ == "__main__":
    # Example 1: Valid product
    valid_product = {
        "id": "PROD-001",
        "title": "Premium Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "category": "Electronics",
        "sku": "SKU-WH-001",
        "brand": "AudioPro",
        "product_url": "https://example.com/products/headphones",
        "image_url": "https://example.com/images/headphones.jpg",
        "price": 149.99,
        "currency": "USD",
        "availability": "in_stock",
        "stock_quantity": 50,
        "delivery_time_days": 2,
        "rating": 4.5,
        "review_count": 125,
        "color": "Black",
        "material": "Aluminum and Plastic",
        "warranty": "1 year manufacturer warranty",
        "seller_name": "TechStore",
        "is_active": True,
    }
    
    # Example 2: Invalid product (missing required fields)
    invalid_product = {
        "id": "PROD-002",
        "title": "Basic Headphones",
        # Missing category, price, currency
    }
    
    # Validate products
    is_valid, errors = ChatGPTFeedSpec.validate_product(valid_product)
    print(f"Valid Product: {is_valid}")
    if errors:
        print(f"Errors: {errors}\n")
    
    is_valid, errors = ChatGPTFeedSpec.validate_product(invalid_product)
    print(f"Invalid Product: {is_valid}")
    print(f"Errors: {errors}\n")
    
    # Print specification summary
    summary = ChatGPTFeedSpec.get_spec_summary()
    print("Feed Specification Summary:")
    print(f"Total Fields: {summary['total_fields']}")
    print(f"Required Fields: {len(summary['required_fields'])}")
    print(f"Optional Fields: {len(summary['optional_fields'])}")
    print(f"Field Types: {summary['field_count_by_type']}")
    print(f"Dependencies: {summary['dependencies_count']}")
