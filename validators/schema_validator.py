"""
Schema Validator for ChatGPT Product Feeds

This module provides comprehensive schema validation logic for product feed data.
It validates the structure, data types, and business rules for ChatGPT product feeds.

Author: deepakgargct
Date: 2026-01-06
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime


class ValidationStatus(Enum):
    """Enumeration of validation status codes."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"


class FieldType(Enum):
    """Enumeration of supported field data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    EMAIL = "email"
    URL = "url"
    CURRENCY = "currency"


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    severity: ValidationStatus
    value: Optional[Any] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        """Return string representation of validation error."""
        return f"[{self.severity.value.upper()}] {self.field}: {self.message}"


@dataclass
class ValidationResult:
    """Represents the result of schema validation."""
    is_valid: bool
    status: ValidationStatus
    errors: List[ValidationError]
    warnings: List[ValidationError]
    validated_data: Optional[Dict[str, Any]] = None
    validation_time_ms: float = 0.0

    def get_error_summary(self) -> str:
        """Return a summary of validation errors."""
        summary = f"Validation Status: {self.status.value}\n"
        summary += f"Errors: {len(self.errors)}\n"
        summary += f"Warnings: {len(self.warnings)}\n"
        
        if self.errors:
            summary += "\nErrors:\n"
            for error in self.errors:
                summary += f"  - {error}\n"
        
        if self.warnings:
            summary += "\nWarnings:\n"
            for warning in self.warnings:
                summary += f"  - {warning}\n"
        
        return summary


class FieldValidator:
    """Validator for individual fields."""

    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: int = None,
                       pattern: str = None, allowed_values: List[str] = None) -> Tuple[bool, Optional[str]]:
        """Validate string field."""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        
        if len(value) < min_length:
            return False, f"String length {len(value)} is less than minimum {min_length}"
        
        if max_length and len(value) > max_length:
            return False, f"String length {len(value)} exceeds maximum {max_length}"
        
        if pattern and not re.match(pattern, value):
            return False, f"String does not match required pattern: {pattern}"
        
        if allowed_values and value not in allowed_values:
            return False, f"Value must be one of: {', '.join(allowed_values)}"
        
        return True, None

    @staticmethod
    def validate_integer(value: Any, min_value: int = None, max_value: int = None) -> Tuple[bool, Optional[str]]:
        """Validate integer field."""
        if not isinstance(value, int) or isinstance(value, bool):
            return False, f"Expected integer, got {type(value).__name__}"
        
        if min_value is not None and value < min_value:
            return False, f"Value {value} is less than minimum {min_value}"
        
        if max_value is not None and value > max_value:
            return False, f"Value {value} exceeds maximum {max_value}"
        
        return True, None

    @staticmethod
    def validate_float(value: Any, min_value: float = None, max_value: float = None) -> Tuple[bool, Optional[str]]:
        """Validate float field."""
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Expected float, got {type(value).__name__}"
        
        if min_value is not None and float(value) < min_value:
            return False, f"Value {value} is less than minimum {min_value}"
        
        if max_value is not None and float(value) > max_value:
            return False, f"Value {value} exceeds maximum {max_value}"
        
        return True, None

    @staticmethod
    def validate_boolean(value: Any) -> Tuple[bool, Optional[str]]:
        """Validate boolean field."""
        if not isinstance(value, bool):
            return False, f"Expected boolean, got {type(value).__name__}"
        return True, None

    @staticmethod
    def validate_email(value: Any) -> Tuple[bool, Optional[str]]:
        """Validate email field."""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return False, "Invalid email format"
        
        return True, None

    @staticmethod
    def validate_url(value: Any) -> Tuple[bool, Optional[str]]:
        """Validate URL field."""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        if not re.match(pattern, value):
            return False, "Invalid URL format"
        
        return True, None

    @staticmethod
    def validate_datetime(value: Any, format_str: str = "%Y-%m-%d %H:%M:%S") -> Tuple[bool, Optional[str]]:
        """Validate datetime field."""
        if isinstance(value, datetime):
            return True, None
        
        if not isinstance(value, str):
            return False, f"Expected string or datetime, got {type(value).__name__}"
        
        try:
            datetime.strptime(value, format_str)
            return True, None
        except ValueError:
            return False, f"Invalid datetime format. Expected: {format_str}"

    @staticmethod
    def validate_currency(value: Any, min_value: float = 0) -> Tuple[bool, Optional[str]]:
        """Validate currency field."""
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Expected number, got {type(value).__name__}"
        
        if value < min_value:
            return False, f"Currency value {value} cannot be less than {min_value}"
        
        if round(value, 2) != value:
            return False, "Currency must have at most 2 decimal places"
        
        return True, None


class SchemaValidator:
    """Main schema validator for product feeds."""

    def __init__(self):
        """Initialize the schema validator."""
        self.field_validator = FieldValidator()
        self.schema_rules = self._define_schema_rules()

    def _define_schema_rules(self) -> Dict[str, Dict[str, Any]]:
        """Define schema validation rules for product feed fields."""
        return {
            "product_id": {
                "type": FieldType.STRING,
                "required": True,
                "min_length": 1,
                "max_length": 100,
                "description": "Unique identifier for the product",
            },
            "product_name": {
                "type": FieldType.STRING,
                "required": True,
                "min_length": 1,
                "max_length": 200,
                "description": "Name of the product",
            },
            "description": {
                "type": FieldType.STRING,
                "required": False,
                "min_length": 0,
                "max_length": 5000,
                "description": "Detailed product description",
            },
            "category": {
                "type": FieldType.STRING,
                "required": True,
                "allowed_values": ["Electronics", "Books", "Clothing", "Home", "Sports", "Other"],
                "description": "Product category",
            },
            "price": {
                "type": FieldType.CURRENCY,
                "required": True,
                "min_value": 0,
                "description": "Product price",
            },
            "currency": {
                "type": FieldType.STRING,
                "required": False,
                "allowed_values": ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"],
                "description": "Currency code",
            },
            "rating": {
                "type": FieldType.FLOAT,
                "required": False,
                "min_value": 0,
                "max_value": 5,
                "description": "Product rating (0-5)",
            },
            "review_count": {
                "type": FieldType.INTEGER,
                "required": False,
                "min_value": 0,
                "description": "Number of reviews",
            },
            "in_stock": {
                "type": FieldType.BOOLEAN,
                "required": False,
                "description": "Stock availability status",
            },
            "url": {
                "type": FieldType.URL,
                "required": False,
                "description": "Product URL",
            },
            "image_url": {
                "type": FieldType.URL,
                "required": False,
                "description": "Product image URL",
            },
            "sku": {
                "type": FieldType.STRING,
                "required": False,
                "min_length": 1,
                "max_length": 50,
                "description": "Stock Keeping Unit",
            },
            "manufacturer": {
                "type": FieldType.STRING,
                "required": False,
                "min_length": 1,
                "max_length": 200,
                "description": "Product manufacturer",
            },
            "tags": {
                "type": FieldType.ARRAY,
                "required": False,
                "description": "Product tags for categorization",
            },
            "created_at": {
                "type": FieldType.DATETIME,
                "required": False,
                "description": "Product creation timestamp",
            },
            "updated_at": {
                "type": FieldType.DATETIME,
                "required": False,
                "description": "Product last update timestamp",
            },
        }

    def validate_field(self, field_name: str, value: Any,
                      custom_rules: Dict[str, Any] = None) -> Tuple[bool, Optional[str]]:
        """Validate a single field against schema rules."""
        rules = custom_rules or self.schema_rules.get(field_name, {})
        
        if not rules:
            return True, None

        field_type = rules.get("type", FieldType.STRING)

        # Type validation
        if field_type == FieldType.STRING:
            valid, error = self.field_validator.validate_string(
                value,
                min_length=rules.get("min_length", 0),
                max_length=rules.get("max_length"),
                pattern=rules.get("pattern"),
                allowed_values=rules.get("allowed_values"),
            )
        elif field_type == FieldType.INTEGER:
            valid, error = self.field_validator.validate_integer(
                value,
                min_value=rules.get("min_value"),
                max_value=rules.get("max_value"),
            )
        elif field_type == FieldType.FLOAT:
            valid, error = self.field_validator.validate_float(
                value,
                min_value=rules.get("min_value"),
                max_value=rules.get("max_value"),
            )
        elif field_type == FieldType.BOOLEAN:
            valid, error = self.field_validator.validate_boolean(value)
        elif field_type == FieldType.EMAIL:
            valid, error = self.field_validator.validate_email(value)
        elif field_type == FieldType.URL:
            valid, error = self.field_validator.validate_url(value)
        elif field_type == FieldType.DATETIME:
            valid, error = self.field_validator.validate_datetime(
                value,
                format_str=rules.get("format", "%Y-%m-%d %H:%M:%S"),
            )
        elif field_type == FieldType.CURRENCY:
            valid, error = self.field_validator.validate_currency(
                value,
                min_value=rules.get("min_value", 0),
            )
        elif field_type == FieldType.ARRAY:
            valid, error = isinstance(value, list), None if isinstance(value, list) else f"Expected array, got {type(value).__name__}"
        elif field_type == FieldType.OBJECT:
            valid, error = isinstance(value, dict), None if isinstance(value, dict) else f"Expected object, got {type(value).__name__}"
        else:
            valid, error = True, None

        return valid, error

    def validate_product(self, product_data: Dict[str, Any]) -> ValidationResult:
        """Validate a complete product record."""
        import time
        start_time = time.time()
        
        errors = []
        warnings = []
        is_valid = True

        # Check for required fields
        for field_name, rules in self.schema_rules.items():
            if rules.get("required", False) and field_name not in product_data:
                is_valid = False
                errors.append(ValidationError(
                    field=field_name,
                    message=f"Required field '{field_name}' is missing",
                    severity=ValidationStatus.ERROR,
                    suggestion=f"Add the required field '{field_name}' to the product data",
                ))

        # Validate existing fields
        for field_name, value in product_data.items():
            if field_name not in self.schema_rules:
                warnings.append(ValidationError(
                    field=field_name,
                    message=f"Unknown field '{field_name}' in product data",
                    severity=ValidationStatus.WARNING,
                ))
                continue

            valid, error_msg = self.validate_field(field_name, value)
            if not valid:
                is_valid = False
                errors.append(ValidationError(
                    field=field_name,
                    message=error_msg,
                    severity=ValidationStatus.ERROR,
                    value=value,
                ))

        # Business logic validations
        if "price" in product_data and "currency" not in product_data:
            warnings.append(ValidationError(
                field="currency",
                message="Currency not specified for price",
                severity=ValidationStatus.WARNING,
                suggestion="Add 'currency' field to clarify the price currency",
            ))

        if "rating" in product_data and "review_count" in product_data:
            if product_data["rating"] > 0 and product_data["review_count"] == 0:
                warnings.append(ValidationError(
                    field="review_count",
                    message="Product has a rating but no reviews",
                    severity=ValidationStatus.WARNING,
                ))

        end_time = time.time()
        validation_time_ms = (end_time - start_time) * 1000

        status = ValidationStatus.VALID if is_valid else ValidationStatus.INVALID

        return ValidationResult(
            is_valid=is_valid,
            status=status,
            errors=errors,
            warnings=warnings,
            validated_data=product_data if is_valid else None,
            validation_time_ms=validation_time_ms,
        )

    def validate_batch(self, products: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate a batch of product records."""
        results = []
        for product in products:
            results.append(self.validate_product(product))
        return results

    def get_schema_documentation(self) -> str:
        """Generate documentation for the schema."""
        doc = "# Product Feed Schema Documentation\n\n"
        doc += "## Field Definitions\n\n"
        
        for field_name, rules in self.schema_rules.items():
            doc += f"### {field_name}\n"
            doc += f"- **Type**: {rules.get('type', FieldType.STRING).value}\n"
            doc += f"- **Required**: {'Yes' if rules.get('required', False) else 'No'}\n"
            doc += f"- **Description**: {rules.get('description', 'N/A')}\n"
            
            if "min_length" in rules:
                doc += f"- **Min Length**: {rules['min_length']}\n"
            if "max_length" in rules:
                doc += f"- **Max Length**: {rules['max_length']}\n"
            if "min_value" in rules:
                doc += f"- **Min Value**: {rules['min_value']}\n"
            if "max_value" in rules:
                doc += f"- **Max Value**: {rules['max_value']}\n"
            if "allowed_values" in rules:
                doc += f"- **Allowed Values**: {', '.join(rules['allowed_values'])}\n"
            
            doc += "\n"
        
        return doc
