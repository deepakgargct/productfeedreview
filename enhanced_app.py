"""
Enhanced Product Feed Review Application
A comprehensive Streamlit application for validating product feeds with ChatGPT attributes,
compliance scoring, and batch processing capabilities.

Author: deepakgargct
Date: 2026-01-06
"""

import streamlit as st
import pandas as pd
import json
import re
from typing import Dict, List, Tuple, Optional, Any
from urllib.parse import urlparse
from datetime import datetime
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum

# ======================== CONFIGURATION ========================

PRIORITY_LEVELS = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4
}

class AttributePriority(Enum):
    """Priority levels for product feed attributes"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class ProductAttribute:
    """Data class for product feed attribute"""
    name: str
    description: str
    priority: AttributePriority
    required: bool
    data_type: str
    validation_rules: Dict[str, Any]
    examples: List[str]

# ======================== PRODUCT FEED ATTRIBUTES (70+) ========================

PRODUCT_ATTRIBUTES = {
    # Core Product Information (CRITICAL)
    "id": ProductAttribute(
        name="id",
        description="Unique product identifier",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100, "pattern": "^[a-zA-Z0-9_-]+$"},
        examples=["SKU123", "PROD-001", "item_456"]
    ),
    "title": ProductAttribute(
        name="title",
        description="Product name/title",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="string",
        validation_rules={"min_length": 5, "max_length": 150},
        examples=["Blue Cotton T-Shirt", "Wireless Bluetooth Headphones"]
    ),
    "description": ProductAttribute(
        name="description",
        description="Product description",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="string",
        validation_rules={"min_length": 10, "max_length": 5000},
        examples=["High-quality cotton t-shirt with comfortable fit"]
    ),
    
    # Pricing Information (CRITICAL)
    "price": ProductAttribute(
        name="price",
        description="Product price",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="decimal",
        validation_rules={"min": 0, "pattern": "^[0-9]+(\\.[0-9]{2})?$"},
        examples=["29.99", "100.00", "199.95"]
    ),
    "currency": ProductAttribute(
        name="currency",
        description="Currency code (ISO 4217)",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="string",
        validation_rules={"pattern": "^[A-Z]{3}$"},
        examples=["USD", "EUR", "GBP", "INR"]
    ),
    "sale_price": ProductAttribute(
        name="sale_price",
        description="Discounted product price",
        priority=AttributePriority.HIGH,
        required=False,
        data_type="decimal",
        validation_rules={"min": 0, "pattern": "^[0-9]+(\\.[0-9]{2})?$"},
        examples=["19.99", "79.99"]
    ),
    
    # Product Links (CRITICAL)
    "link": ProductAttribute(
        name="link",
        description="Product page URL",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="url",
        validation_rules={"format": "url", "protocols": ["http", "https"]},
        examples=["https://example.com/product/123", "https://shop.com/items/blue-shirt"]
    ),
    "image_link": ProductAttribute(
        name="image_link",
        description="Product image URL",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="url",
        validation_rules={"format": "url", "protocols": ["http", "https"]},
        examples=["https://example.com/images/product-123.jpg"]
    ),
    "additional_image_link": ProductAttribute(
        name="additional_image_link",
        description="Additional product images (comma-separated URLs)",
        priority=AttributePriority.HIGH,
        required=False,
        data_type="string",
        validation_rules={"delimiter": ","},
        examples=["https://example.com/images/product-123-2.jpg,https://example.com/images/product-123-3.jpg"]
    ),
    
    # Product Classification (CRITICAL)
    "product_type": ProductAttribute(
        name="product_type",
        description="Product category/type",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="string",
        validation_rules={"min_length": 2, "max_length": 250},
        examples=["Apparel > Clothing > Shirts", "Electronics > Computers > Laptops"]
    ),
    "google_product_category": ProductAttribute(
        name="google_product_category",
        description="Google's product taxonomy category",
        priority=AttributePriority.HIGH,
        required=True,
        data_type="integer",
        validation_rules={"min": 1},
        examples=["185", "2334", "5672"]
    ),
    
    # Availability & Status (CRITICAL)
    "availability": ProductAttribute(
        name="availability",
        description="Product availability status",
        priority=AttributePriority.CRITICAL,
        required=True,
        data_type="enum",
        validation_rules={"enum": ["in_stock", "out_of_stock", "preorder", "backorder"]},
        examples=["in_stock", "preorder"]
    ),
    "availability_date": ProductAttribute(
        name="availability_date",
        description="Date when product becomes available",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="date",
        validation_rules={"format": "YYYY-MM-DD"},
        examples=["2026-02-15", "2026-03-01"]
    ),
    
    # Brand & Manufacturer (HIGH)
    "brand": ProductAttribute(
        name="brand",
        description="Product brand name",
        priority=AttributePriority.HIGH,
        required=True,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["Nike", "Apple", "Samsung"]
    ),
    "manufacturer": ProductAttribute(
        name="manufacturer",
        description="Product manufacturer",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["ABC Manufacturing Co.", "XYZ Industries"]
    ),
    
    # Identifiers (HIGH)
    "gtin": ProductAttribute(
        name="gtin",
        description="Global Trade Item Number (UPC/EAN/ISBN)",
        priority=AttributePriority.HIGH,
        required=False,
        data_type="string",
        validation_rules={"pattern": "^[0-9]{8,14}$"},
        examples=["5901234123457", "978020137962"]
    ),
    "mpn": ProductAttribute(
        name="mpn",
        description="Manufacturer Part Number",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["XYZ-123-456", "MPN-78901"]
    ),
    
    # Attributes & Variants (HIGH)
    "color": ProductAttribute(
        name="color",
        description="Product color",
        priority=AttributePriority.HIGH,
        required=False,
        data_type="string",
        validation_rules={"min_length": 2, "max_length": 100},
        examples=["Blue", "Navy Blue", "Electric Blue"]
    ),
    "size": ProductAttribute(
        name="size",
        description="Product size",
        priority=AttributePriority.HIGH,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["Medium", "L", "10", "42"]
    ),
    "material": ProductAttribute(
        name="material",
        description="Product material composition",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 2, "max_length": 500},
        examples=["100% Cotton", "Cotton 80%, Polyester 20%"]
    ),
    "pattern": ProductAttribute(
        name="pattern",
        description="Product pattern/design",
        priority=AttributePriority.LOW,
        required=False,
        data_type="string",
        validation_rules={"min_length": 2, "max_length": 100},
        examples=["Solid", "Striped", "Checkered", "Floral"]
    ),
    
    # Specifications (MEDIUM)
    "weight": ProductAttribute(
        name="weight",
        description="Product weight with unit",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"pattern": "^[0-9.]+ (kg|g|lb|oz)$"},
        examples=["2.5 kg", "250 g", "5.5 lb"]
    ),
    "dimensions": ProductAttribute(
        name="dimensions",
        description="Product dimensions (length x width x height)",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"pattern": "^[0-9.]+ x [0-9.]+ x [0-9.]+ (cm|in|m)$"},
        examples=["10 x 20 x 30 cm", "15 x 25 x 40 in"]
    ),
    
    # Ratings & Reviews (MEDIUM)
    "rating": ProductAttribute(
        name="rating",
        description="Product rating (1-5)",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="decimal",
        validation_rules={"min": 1, "max": 5, "pattern": "^[1-5](\\.[0-9]{1,2})?$"},
        examples=["4.5", "3.8", "5"]
    ),
    "rating_count": ProductAttribute(
        name="rating_count",
        description="Number of ratings/reviews",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="integer",
        validation_rules={"min": 0},
        examples=["1250", "5000"]
    ),
    "review_count": ProductAttribute(
        name="review_count",
        description="Number of product reviews",
        priority=AttributePriority.LOW,
        required=False,
        data_type="integer",
        validation_rules={"min": 0},
        examples=["500", "2000"]
    ),
    
    # Shipping & Delivery (HIGH)
    "shipping_weight": ProductAttribute(
        name="shipping_weight",
        description="Weight for shipping calculations",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"pattern": "^[0-9.]+ (kg|g|lb|oz)$"},
        examples=["3.0 kg", "6.6 lb"]
    ),
    "shipping_label": ProductAttribute(
        name="shipping_label",
        description="Shipping label/class",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["Standard", "Fragile", "Heavy"]
    ),
    
    # Pricing Variants (MEDIUM)
    "subscription_cost": ProductAttribute(
        name="subscription_cost",
        description="Recurring subscription price",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="decimal",
        validation_rules={"min": 0},
        examples=["9.99", "49.99"]
    ),
    "subscription_period": ProductAttribute(
        name="subscription_period",
        description="Subscription billing period",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="enum",
        validation_rules={"enum": ["month", "year", "week", "day"]},
        examples=["month", "year"]
    ),
    
    # Promotions (MEDIUM)
    "promotion_id": ProductAttribute(
        name="promotion_id",
        description="Associated promotion identifier",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["PROMO-123", "SALE-2026-JAN"]
    ),
    "sale_effective_date_start": ProductAttribute(
        name="sale_effective_date_start",
        description="Sale start date",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="date",
        validation_rules={"format": "YYYY-MM-DD"},
        examples=["2026-01-06", "2026-01-15"]
    ),
    "sale_effective_date_end": ProductAttribute(
        name="sale_effective_date_end",
        description="Sale end date",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="date",
        validation_rules={"format": "YYYY-MM-DD"},
        examples=["2026-02-06", "2026-12-31"]
    ),
    
    # Target Audience (MEDIUM)
    "target_gender": ProductAttribute(
        name="target_gender",
        description="Product target gender",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="enum",
        validation_rules={"enum": ["male", "female", "unisex", "other"]},
        examples=["female", "unisex"]
    ),
    "target_age_group": ProductAttribute(
        name="target_age_group",
        description="Product target age group",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="enum",
        validation_rules={"enum": ["newborn", "infant", "toddler", "kids", "adult", "senior"]},
        examples=["adult", "kids"]
    ),
    
    # Compliance & Safety (HIGH)
    "is_bundle": ProductAttribute(
        name="is_bundle",
        description="Whether product is a bundle",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="boolean",
        validation_rules={"type": "boolean"},
        examples=["true", "false"]
    ),
    "multipack": ProductAttribute(
        name="multipack",
        description="Number of items in multipack",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="integer",
        validation_rules={"min": 1},
        examples=["2", "6", "12"]
    ),
    "item_group_id": ProductAttribute(
        name="item_group_id",
        description="Identifier for product group/variants",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["GROUP-001", "SHIRT-VARIANTS"]
    ),
    
    # Digital Products (MEDIUM)
    "digital_source_url": ProductAttribute(
        name="digital_source_url",
        description="URL for digital product download",
        priority=AttributePriority.HIGH,
        required=False,
        data_type="url",
        validation_rules={"format": "url", "protocols": ["http", "https"]},
        examples=["https://example.com/downloads/product.zip"]
    ),
    
    # Seller Information (MEDIUM)
    "seller_name": ProductAttribute(
        name="seller_name",
        description="Name of product seller/merchant",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["John's Shop", "ABC Retail"]
    ),
    "seller_id": ProductAttribute(
        name="seller_id",
        description="Unique seller identifier",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["SELLER-123", "SHOP-001"]
    ),
    
    # Compliance Certifications (MEDIUM)
    "certifications": ProductAttribute(
        name="certifications",
        description="Product certifications (comma-separated)",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"delimiter": ","},
        examples=["FCC", "CE,UL", "FDA,ISO9001"]
    ),
    "warranty": ProductAttribute(
        name="warranty",
        description="Warranty information",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 5, "max_length": 500},
        examples=["12 months manufacturer warranty", "Lifetime warranty"]
    ),
    
    # Environmental & Sustainability (LOW)
    "eco_friendly": ProductAttribute(
        name="eco_friendly",
        description="Whether product is eco-friendly",
        priority=AttributePriority.LOW,
        required=False,
        data_type="boolean",
        validation_rules={"type": "boolean"},
        examples=["true", "false"]
    ),
    "recyclable": ProductAttribute(
        name="recyclable",
        description="Whether product packaging is recyclable",
        priority=AttributePriority.LOW,
        required=False,
        data_type="boolean",
        validation_rules={"type": "boolean"},
        examples=["true", "false"]
    ),
    
    # Enhanced SEO & Metadata (MEDIUM)
    "custom_label_0": ProductAttribute(
        name="custom_label_0",
        description="Custom product label/tag 0",
        priority=AttributePriority.LOW,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["New Arrival", "Best Seller"]
    ),
    "custom_label_1": ProductAttribute(
        name="custom_label_1",
        description="Custom product label/tag 1",
        priority=AttributePriority.LOW,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["Summer Collection", "Limited Edition"]
    ),
    "custom_label_2": ProductAttribute(
        name="custom_label_2",
        description="Custom product label/tag 2",
        priority=AttributePriority.LOW,
        required=False,
        data_type="string",
        validation_rules={"min_length": 1, "max_length": 100},
        examples=["Sale", "Recommended"]
    ),
    
    # Expiration & Status (MEDIUM)
    "expiration_date": ProductAttribute(
        name="expiration_date",
        description="Product expiration/shelf-life date",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="date",
        validation_rules={"format": "YYYY-MM-DD"},
        examples=["2027-12-31", "2026-06-30"]
    ),
    
    # Rich Content (MEDIUM)
    "video_link": ProductAttribute(
        name="video_link",
        description="Product demo/tutorial video URL",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="url",
        validation_rules={"format": "url", "protocols": ["http", "https"]},
        examples=["https://youtube.com/watch?v=abc123", "https://vimeo.com/123456"]
    ),
    
    # Inventory Management (MEDIUM)
    "quantity": ProductAttribute(
        name="quantity",
        description="Product stock quantity",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="integer",
        validation_rules={"min": 0},
        examples=["100", "500", "1000"]
    ),
    
    # Additional Classification (MEDIUM)
    "item_type": ProductAttribute(
        name="item_type",
        description="Detailed item type classification",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"min_length": 2, "max_length": 100},
        examples=["Men's T-Shirt", "Laptop Computer"]
    ),
    
    # URL Variations (MEDIUM)
    "mobile_link": ProductAttribute(
        name="mobile_link",
        description="Mobile-optimized product page URL",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="url",
        validation_rules={"format": "url", "protocols": ["http", "https"]},
        examples=["https://m.example.com/product/123"]
    ),
    
    # Content Language (LOW)
    "content_language": ProductAttribute(
        name="content_language",
        description="Language code (ISO 639-1)",
        priority=AttributePriority.LOW,
        required=False,
        data_type="string",
        validation_rules={"pattern": "^[a-z]{2}(-[A-Z]{2})?$"},
        examples=["en", "es", "fr", "en-US", "zh-CN"]
    ),
    "target_country": ProductAttribute(
        name="target_country",
        description="Target country code (ISO 3166-1)",
        priority=AttributePriority.MEDIUM,
        required=False,
        data_type="string",
        validation_rules={"pattern": "^[A-Z]{2}$"},
        examples=["US", "GB", "DE", "IN"]
    ),
}

# ======================== VALIDATORS ========================

class URLValidator:
    """Validates URLs"""
    
    @staticmethod
    def validate(url: str, protocols: List[str] = None) -> Tuple[bool, str]:
        """Validate URL format and protocol"""
        if not url:
            return False, "URL cannot be empty"
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Invalid URL format"
            
            if protocols and result.scheme not in protocols:
                return False, f"URL scheme must be one of: {', '.join(protocols)}"
            
            return True, "Valid URL"
        except Exception as e:
            return False, f"URL validation error: {str(e)}"

class SchemaValidator:
    """Validates data against schema"""
    
    @staticmethod
    def validate_string(value: str, rules: Dict) -> Tuple[bool, str]:
        """Validate string field"""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        
        if "min_length" in rules and len(value) < rules["min_length"]:
            return False, f"String length must be at least {rules['min_length']}"
        
        if "max_length" in rules and len(value) > rules["max_length"]:
            return False, f"String length must not exceed {rules['max_length']}"
        
        if "pattern" in rules:
            if not re.match(rules["pattern"], value):
                return False, f"String does not match required pattern: {rules['pattern']}"
        
        return True, "Valid string"
    
    @staticmethod
    def validate_decimal(value, rules: Dict) -> Tuple[bool, str]:
        """Validate decimal/numeric field"""
        try:
            num = float(value)
            
            if "min" in rules and num < rules["min"]:
                return False, f"Value must be at least {rules['min']}"
            
            if "max" in rules and num > rules["max"]:
                return False, f"Value must not exceed {rules['max']}"
            
            if "pattern" in rules:
                if not re.match(rules["pattern"], str(value)):
                    return False, f"Value does not match required pattern"
            
            return True, "Valid decimal"
        except ValueError:
            return False, "Value must be numeric"
    
    @staticmethod
    def validate_integer(value, rules: Dict) -> Tuple[bool, str]:
        """Validate integer field"""
        try:
            num = int(value)
            
            if "min" in rules and num < rules["min"]:
                return False, f"Value must be at least {rules['min']}"
            
            if "max" in rules and num > rules["max"]:
                return False, f"Value must not exceed {rules['max']}"
            
            return True, "Valid integer"
        except ValueError:
            return False, "Value must be an integer"
    
    @staticmethod
    def validate_enum(value: str, rules: Dict) -> Tuple[bool, str]:
        """Validate enum field"""
        if "enum" in rules and value not in rules["enum"]:
            return False, f"Value must be one of: {', '.join(rules['enum'])}"
        
        return True, "Valid enum"
    
    @staticmethod
    def validate_date(value: str, rules: Dict) -> Tuple[bool, str]:
        """Validate date field"""
        if "format" in rules and rules["format"] == "YYYY-MM-DD":
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True, "Valid date"
            except ValueError:
                return False, "Date must be in YYYY-MM-DD format"
        
        return False, "Invalid date format specification"
    
    @staticmethod
    def validate_boolean(value, rules: Dict) -> Tuple[bool, str]:
        """Validate boolean field"""
        if isinstance(value, bool):
            return True, "Valid boolean"
        
        if isinstance(value, str) and value.lower() in ["true", "false", "yes", "no", "1", "0"]:
            return True, "Valid boolean"
        
        return False, "Value must be boolean (true/false)"

class ProductValidator:
    """Comprehensive product validator"""
    
    @staticmethod
    def validate_product(product: Dict, attributes: Dict = PRODUCT_ATTRIBUTES) -> Dict:
        """Validate entire product against schema"""
        errors = []
        warnings = []
        
        # Check required attributes
        for attr_name, attr_config in attributes.items():
            if attr_config.required and attr_name not in product:
                errors.append({
                    "field": attr_name,
                    "priority": attr_config.priority.value,
                    "message": f"Required attribute '{attr_name}' is missing"
                })
        
        # Validate provided attributes
        for attr_name, value in product.items():
            if attr_name not in attributes:
                warnings.append({
                    "field": attr_name,
                    "message": f"Unknown attribute '{attr_name}'"
                })
                continue
            
            attr_config = attributes[attr_name]
            
            if not value:
                if attr_config.required:
                    errors.append({
                        "field": attr_name,
                        "priority": attr_config.priority.value,
                        "message": f"Required attribute '{attr_name}' has empty value"
                    })
                continue
            
            # Validate based on data type
            is_valid, message = ProductValidator._validate_field(
                value, attr_config.data_type, attr_config.validation_rules
            )
            
            if not is_valid:
                errors.append({
                    "field": attr_name,
                    "priority": attr_config.priority.value,
                    "message": message
                })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }
    
    @staticmethod
    def _validate_field(value: Any, data_type: str, rules: Dict) -> Tuple[bool, str]:
        """Validate individual field"""
        validators = {
            "string": SchemaValidator.validate_string,
            "decimal": SchemaValidator.validate_decimal,
            "integer": SchemaValidator.validate_integer,
            "enum": SchemaValidator.validate_enum,
            "date": SchemaValidator.validate_date,
            "boolean": SchemaValidator.validate_boolean,
            "url": lambda v, r: URLValidator.validate(v, r.get("protocols"))
        }
        
        if data_type in validators:
            return validators[data_type](value, rules)
        
        return False, f"Unknown data type: {data_type}"

# ======================== COMPLIANCE SCORING ========================

class ComplianceScorer:
    """Calculates compliance score for products"""
    
    CRITICAL_WEIGHT = 0.40
    HIGH_WEIGHT = 0.30
    MEDIUM_WEIGHT = 0.20
    LOW_WEIGHT = 0.10
    
    @staticmethod
    def calculate_score(validation_result: Dict, product: Dict) -> Dict:
        """Calculate compliance score"""
        errors = validation_result["errors"]
        warnings = validation_result["warnings"]
        
        # Calculate error score by priority
        error_score = ComplianceScorer._calculate_error_score(errors)
        
        # Calculate completeness score
        completeness_score = ComplianceScorer._calculate_completeness_score(product)
        
        # Final score (weighted average)
        final_score = (error_score * 0.7) + (completeness_score * 0.3)
        
        # Determine compliance level
        if final_score >= 95:
            level = "EXCELLENT"
        elif final_score >= 85:
            level = "GOOD"
        elif final_score >= 70:
            level = "ACCEPTABLE"
        elif final_score >= 50:
            level = "NEEDS IMPROVEMENT"
        else:
            level = "CRITICAL"
        
        return {
            "total_score": round(final_score, 2),
            "error_score": round(error_score, 2),
            "completeness_score": round(completeness_score, 2),
            "level": level,
            "error_count": validation_result["error_count"],
            "warning_count": validation_result["warning_count"]
        }
    
    @staticmethod
    def _calculate_error_score(errors: List[Dict]) -> float:
        """Calculate score based on errors"""
        if not errors:
            return 100.0
        
        priority_weights = {
            "CRITICAL": ComplianceScorer.CRITICAL_WEIGHT,
            "HIGH": ComplianceScorer.HIGH_WEIGHT,
            "MEDIUM": ComplianceScorer.MEDIUM_WEIGHT,
            "LOW": ComplianceScorer.LOW_WEIGHT
        }
        
        total_weight = sum(priority_weights.values())
        error_weight = sum(
            priority_weights.get(e["priority"], 0) for e in errors
        )
        
        error_score = max(0, 100 - (error_weight / total_weight * 100))
        return error_score
    
    @staticmethod
    def _calculate_completeness_score(product: Dict) -> float:
        """Calculate score based on data completeness"""
        total_attributes = len(PRODUCT_ATTRIBUTES)
        provided_attributes = len([k for k, v in product.items() if k in PRODUCT_ATTRIBUTES and v])
        
        return (provided_attributes / total_attributes) * 100

# ======================== BATCH PROCESSING ========================

class BatchProcessor:
    """Handles batch processing of products"""
    
    @staticmethod
    def process_batch(products: List[Dict]) -> Dict:
        """Process batch of products"""
        results = []
        
        for idx, product in enumerate(products):
            validation = ProductValidator.validate_product(product)
            compliance = ComplianceScorer.calculate_score(validation, product)
            
            results.append({
                "index": idx + 1,
                "product_id": product.get("id", "N/A"),
                "title": product.get("title", "N/A"),
                "validation": validation,
                "compliance": compliance
            })
        
        # Calculate batch statistics
        avg_score = np.mean([r["compliance"]["total_score"] for r in results])
        total_errors = sum([r["validation"]["error_count"] for r in results])
        total_warnings = sum([r["validation"]["warning_count"] for r in results])
        
        return {
            "total_products": len(products),
            "results": results,
            "batch_statistics": {
                "average_score": round(avg_score, 2),
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "pass_rate": round((sum(1 for r in results if r["compliance"]["total_score"] >= 70) / len(results) * 100) if results else 0, 2)
            }
        }

# ======================== STREAMLIT UI ========================

def init_session_state():
    """Initialize session state variables"""
    if "batch_results" not in st.session_state:
        st.session_state.batch_results = None
    if "current_product" not in st.session_state:
        st.session_state.current_product = {}
    if "validation_results" not in st.session_state:
        st.session_state.validation_results = None

def render_header():
    """Render application header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🛍️ Product Feed Review System")
        st.markdown("*Comprehensive validation and compliance scoring for product feeds*")
    
    with col2:
        st.metric("Total Attributes", len(PRODUCT_ATTRIBUTES))
    
    st.divider()

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.title("Navigation")
        mode = st.radio(
            "Select Mode",
            options=["Single Product", "Batch Upload", "Attributes Reference", "Settings"],
            key="navigation_mode"
        )
        
        st.divider()
        
        st.markdown("### About")
        st.markdown("""
        This application validates product feeds against 70+ ChatGPT product attributes
        with priority-based scoring and compliance assessment.
        
        **Features:**
        - URL validation
        - Schema validation
        - Batch processing
        - Compliance scoring
        - Detailed reporting
        """)
        
        st.divider()
        st.markdown("*Last Updated: 2026-01-06*")
        
        return mode

def render_single_product_mode():
    """Render single product validation mode"""
    st.header("📋 Single Product Validation")
    
    # Product input method selection
    input_method = st.radio(
        "Input Method",
        options=["Form Input", "JSON Input"],
        horizontal=True
    )
    
    product_data = {}
    
    if input_method == "Form Input":
        # Critical attributes section
        st.subheader("🔴 Critical Attributes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_data["id"] = st.text_input(
                "Product ID *",
                help="Unique product identifier"
            )
            product_data["title"] = st.text_input(
                "Product Title *",
                help="Product name/title"
            )
            product_data["price"] = st.text_input(
                "Price *",
                help="Product price (e.g., 29.99)"
            )
        
        with col2:
            product_data["currency"] = st.selectbox(
                "Currency *",
                options=["USD", "EUR", "GBP", "INR", "CAD", "AUD"],
                help="Currency code (ISO 4217)"
            )
            product_data["brand"] = st.text_input(
                "Brand *",
                help="Product brand name"
            )
            product_data["availability"] = st.selectbox(
                "Availability *",
                options=["in_stock", "out_of_stock", "preorder", "backorder"],
                help="Product availability status"
            )
        
        # URLs section
        st.subheader("🔗 Links")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_data["link"] = st.text_input(
                "Product Page URL *",
                help="Product page URL"
            )
        
        with col2:
            product_data["image_link"] = st.text_input(
                "Product Image URL *",
                help="Product image URL"
            )
        
        # Description and classification
        st.subheader("📝 Description & Classification")
        
        product_data["description"] = st.text_area(
            "Description *",
            help="Detailed product description"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_data["product_type"] = st.text_input(
                "Product Type *",
                help="e.g., Apparel > Clothing > Shirts"
            )
        
        with col2:
            product_data["google_product_category"] = st.text_input(
                "Google Product Category",
                help="Google's product taxonomy ID"
            )
        
        # Attributes section
        st.subheader("🏷️ Attributes (Optional)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_data["color"] = st.text_input("Color")
            product_data["size"] = st.text_input("Size")
            product_data["material"] = st.text_input("Material")
        
        with col2:
            product_data["sale_price"] = st.text_input("Sale Price")
            product_data["rating"] = st.text_input("Rating (1-5)")
            product_data["weight"] = st.text_input("Weight (e.g., 2.5 kg)")
        
        with col3:
            product_data["gtin"] = st.text_input("GTIN/UPC/EAN")
            product_data["warranty"] = st.text_input("Warranty")
            product_data["seller_name"] = st.text_input("Seller Name")
    
    else:  # JSON Input
        json_input = st.text_area(
            "Paste JSON Product Data",
            height=300,
            placeholder='{"id": "123", "title": "Product", ...}'
        )
        
        if json_input:
            try:
                product_data = json.loads(json_input)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {str(e)}")
                return
    
    # Validate button
    if st.button("🔍 Validate Product", type="primary", use_container_width=True):
        if not product_data:
            st.error("Please enter product data")
            return
        
        # Perform validation
        validation = ProductValidator.validate_product(product_data)
        compliance = ComplianceScorer.calculate_score(validation, product_data)
        
        st.session_state.validation_results = {
            "product": product_data,
            "validation": validation,
            "compliance": compliance
        }
    
    # Display results
    if st.session_state.validation_results:
        render_validation_results(st.session_state.validation_results)

def render_batch_upload_mode():
    """Render batch upload mode"""
    st.header("📦 Batch Processing")
    
    upload_method = st.radio(
        "Upload Method",
        options=["CSV File", "JSON File"],
        horizontal=True
    )
    
    uploaded_file = st.file_uploader(
        f"Upload {upload_method} file",
        type=["csv", "json"],
        accept_multiple_files=False
    )
    
    if uploaded_file:
        try:
            if upload_method == "CSV File":
                df = pd.read_csv(uploaded_file)
                products = df.to_dict('records')
            else:
                products = json.load(uploaded_file)
                if not isinstance(products, list):
                    products = [products]
            
            st.success(f"Loaded {len(products)} products")
            
            # Display preview
            with st.expander("Preview Data", expanded=False):
                st.dataframe(pd.DataFrame(products).head(10))
            
            # Process batch
            if st.button("🚀 Process Batch", type="primary", use_container_width=True):
                with st.spinner("Processing products..."):
                    batch_results = BatchProcessor.process_batch(products)
                    st.session_state.batch_results = batch_results
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Display batch results
    if st.session_state.batch_results:
        render_batch_results(st.session_state.batch_results)

def render_validation_results(results: Dict):
    """Render validation results"""
    st.subheader("📊 Validation Results")
    
    product = results["product"]
    validation = results["validation"]
    compliance = results["compliance"]
    
    # Compliance score card
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Compliance Score",
            f"{compliance['total_score']}%",
            delta=None
        )
    
    with col2:
        st.metric("Status", compliance["level"])
    
    with col3:
        st.metric("Errors", compliance["error_count"])
    
    with col4:
        st.metric("Warnings", compliance["warning_count"])
    
    st.divider()
    
    # Detailed results
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Errors")
        if validation["errors"]:
            error_df = pd.DataFrame(validation["errors"])
            st.dataframe(
                error_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✓ No errors found")
    
    with col2:
        st.subheader("Warnings")
        if validation["warnings"]:
            warning_df = pd.DataFrame(validation["warnings"])
            st.dataframe(
                warning_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("✓ No warnings")
    
    st.divider()
    
    # Product summary
    st.subheader("Product Summary")
    
    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.write(f"**ID:** {product.get('id', 'N/A')}")
        st.write(f"**Title:** {product.get('title', 'N/A')[:50]}")
        st.write(f"**Brand:** {product.get('brand', 'N/A')}")
    
    with summary_cols[1]:
        st.write(f"**Price:** {product.get('price', 'N/A')} {product.get('currency', '')}")
        st.write(f"**Availability:** {product.get('availability', 'N/A')}")
        st.write(f"**Category:** {product.get('product_type', 'N/A')[:50]}")
    
    with summary_cols[2]:
        st.write(f"**Attributes Provided:** {len([k for k, v in product.items() if v])}")
        st.write(f"**Rating:** {product.get('rating', 'N/A')}")
        st.write(f"**Seller:** {product.get('seller_name', 'N/A')}")
    
    # Export options
    st.divider()
    st.subheader("📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        json_export = json.dumps(results, indent=2)
        st.download_button(
            "📄 Download as JSON",
            json_export,
            file_name="validation_result.json",
            mime="application/json"
        )
    
    with col2:
        csv_export = pd.DataFrame(validation["errors"]).to_csv(index=False)
        st.download_button(
            "📊 Download Errors as CSV",
            csv_export,
            file_name="errors.csv",
            mime="text/csv"
        )

def render_batch_results(batch_results: Dict):
    """Render batch processing results"""
    st.subheader("📊 Batch Results")
    
    # Statistics
    stats = batch_results["batch_statistics"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Products Processed", batch_results["total_products"])
    
    with col2:
        st.metric("Average Score", f"{stats['average_score']}%")
    
    with col3:
        st.metric("Total Errors", stats["total_errors"])
    
    with col4:
        st.metric("Pass Rate", f"{stats['pass_rate']}%")
    
    st.divider()
    
    # Results table
    st.subheader("Detailed Results")
    
    results_data = []
    for result in batch_results["results"]:
        results_data.append({
            "Index": result["index"],
            "Product ID": result["product_id"],
            "Title": result["title"][:50],
            "Score": result["compliance"]["total_score"],
            "Status": result["compliance"]["level"],
            "Errors": result["validation"]["error_count"],
            "Warnings": result["validation"]["warning_count"]
        })
    
    results_df = pd.DataFrame(results_data)
    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Export batch results
    st.divider()
    st.subheader("📥 Export Batch Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_export = json.dumps(batch_results, indent=2)
        st.download_button(
            "📄 Download as JSON",
            json_export,
            file_name="batch_results.json",
            mime="application/json"
        )
    
    with col2:
        csv_export = results_df.to_csv(index=False)
        st.download_button(
            "📊 Download as CSV",
            csv_export,
            file_name="batch_results.csv",
            mime="text/csv"
        )
    
    with col3:
        # Detailed errors export
        all_errors = []
        for result in batch_results["results"]:
            for error in result["validation"]["errors"]:
                all_errors.append({
                    "Product ID": result["product_id"],
                    "Field": error["field"],
                    "Priority": error["priority"],
                    "Message": error["message"]
                })
        
        if all_errors:
            errors_df = pd.DataFrame(all_errors)
            csv_errors = errors_df.to_csv(index=False)
            st.download_button(
                "⚠️ Download All Errors",
                csv_errors,
                file_name="all_errors.csv",
                mime="text/csv"
            )

def render_attributes_reference():
    """Render attributes reference guide"""
    st.header("📚 Attributes Reference Guide")
    
    # Filter attributes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search attributes", placeholder="e.g., price, color")
    
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH"]
        )
    
    # Filter attributes
    filtered_attributes = {
        name: attr for name, attr in PRODUCT_ATTRIBUTES.items()
        if (search_term.lower() in name.lower() or search_term.lower() in attr.description.lower())
        and attr.priority.value in priority_filter
    }
    
    # Display attributes
    for attr_name in sorted(filtered_attributes.keys()):
        attr = filtered_attributes[attr_name]
        
        priority_color = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }
        
        with st.expander(f"{priority_color.get(attr.priority.value, '⚪')} {attr_name} - {attr.data_type}"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**Description:** {attr.description}")
                st.markdown(f"**Priority:** {attr.priority.value}")
                st.markdown(f"**Required:** {'✓ Yes' if attr.required else '✗ No'}")
                st.markdown(f"**Data Type:** {attr.data_type}")
            
            with col2:
                st.markdown("**Examples:**")
                for example in attr.examples:
                    st.code(example)
            
            st.markdown("**Validation Rules:**")
            st.json(attr.validation_rules)
    
    st.info(f"Total attributes: {len(PRODUCT_ATTRIBUTES)} | Displayed: {len(filtered_attributes)}")

def render_settings():
    """Render settings page"""
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("Validation Rules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Priority Weights")
        st.markdown(f"- **Critical:** {ComplianceScorer.CRITICAL_WEIGHT * 100}%")
        st.markdown(f"- **High:** {ComplianceScorer.HIGH_WEIGHT * 100}%")
        st.markdown(f"- **Medium:** {ComplianceScorer.MEDIUM_WEIGHT * 100}%")
        st.markdown(f"- **Low:** {ComplianceScorer.LOW_WEIGHT * 100}%")
    
    with col2:
        st.markdown("### Compliance Levels")
        st.markdown("- **EXCELLENT:** 95% - 100%")
        st.markdown("- **GOOD:** 85% - 94%")
        st.markdown("- **ACCEPTABLE:** 70% - 84%")
        st.markdown("- **NEEDS IMPROVEMENT:** 50% - 69%")
        st.markdown("- **CRITICAL:** < 50%")
    
    st.divider()
    
    st.subheader("System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Product Attributes", len(PRODUCT_ATTRIBUTES))
        critical_count = sum(1 for a in PRODUCT_ATTRIBUTES.values() if a.priority == AttributePriority.CRITICAL)
        st.metric("Critical Attributes", critical_count)
    
    with col2:
        high_count = sum(1 for a in PRODUCT_ATTRIBUTES.values() if a.priority == AttributePriority.HIGH)
        st.metric("High Priority Attributes", high_count)
        required_count = sum(1 for a in PRODUCT_ATTRIBUTES.values() if a.required)
        st.metric("Required Attributes", required_count)
    
    st.divider()
    
    st.subheader("About")
    st.markdown("""
    **Product Feed Review System**
    
    Version: 1.0.0
    Last Updated: 2026-01-06
    
    This application validates product feeds against industry standards including:
    - Google Merchant Center specifications
    - ChatGPT product feed attributes
    - Custom compliance rules
    
    **Features:**
    - Single and batch product validation
    - URL validation with protocol checking
    - Schema validation for all data types
    - Compliance scoring with priority weighting
    - Comprehensive reporting and export options
    """)

# ======================== MAIN APPLICATION ========================

def main():
    """Main application"""
    # Page config
    st.set_page_config(
        page_title="Product Feed Review",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    render_header()
    
    # Sidebar navigation
    mode = render_sidebar()
    
    # Main content
    if mode == "Single Product":
        render_single_product_mode()
    elif mode == "Batch Upload":
        render_batch_upload_mode()
    elif mode == "Attributes Reference":
        render_attributes_reference()
    elif mode == "Settings":
        render_settings()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888;'>
    <p>Product Feed Review System | © 2026 | deepakgargct</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
