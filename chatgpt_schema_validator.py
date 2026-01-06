"""
ChatGPT Schema Validator

Comprehensive validator module for ChatGPT product feed schema.
Provides field-level and schema-level validation with detailed reporting.

Features:
- Field-level validation with type checking
- Schema-level validation for dependencies
- Detailed validation reports with errors and warnings
- Batch validation for multiple products
- Support for ChatGPT product feed specification

Author: deepakgargct
Created: 2026-01-06
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import re
import json
from datetime import datetime


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    severity: ValidationSeverity
    field_name: str
    message: str
    value: Optional[Any] = None
    suggestion: Optional[str] = None
    rule: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "severity": self.severity.value,
            "field_name": self.field_name,
            "message": self.message,
            "value": self.value,
            "suggestion": self.suggestion,
            "rule": self.rule
        }


@dataclass
class FieldValidationResult:
    """Result of field-level validation"""
    field_name: str
    is_valid: bool
    value: Any
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_error(self, message: str, suggestion: Optional[str] = None, rule: Optional[str] = None) -> None:
        """Add an error to this field validation"""
        self.is_valid = False
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR,
            field_name=self.field_name,
            message=message,
            value=self.value,
            suggestion=suggestion,
            rule=rule
        ))
    
    def add_warning(self, message: str, suggestion: Optional[str] = None, rule: Optional[str] = None) -> None:
        """Add a warning to this field validation"""
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            field_name=self.field_name,
            message=message,
            value=self.value,
            suggestion=suggestion,
            rule=rule
        ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field_name": self.field_name,
            "is_valid": self.is_valid,
            "value": self.value,
            "issues": [issue.to_dict() for issue in self.issues]
        }


@dataclass
class ProductValidationResult:
    """Result of product-level validation"""
    product_id: str
    is_valid: bool
    field_results: Dict[str, FieldValidationResult] = field(default_factory=dict)
    schema_issues: List[ValidationIssue] = field(default_factory=list)
    score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_field_result(self, result: FieldValidationResult) -> None:
        """Add a field validation result"""
        self.field_results[result.field_name] = result
        if not result.is_valid:
            self.is_valid = False
    
    def add_schema_issue(self, issue: ValidationIssue) -> None:
        """Add a schema-level issue"""
        self.schema_issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.is_valid = False
    
    def get_all_errors(self) -> List[ValidationIssue]:
        """Get all errors from field and schema validation"""
        errors = []
        for result in self.field_results.values():
            errors.extend([i for i in result.issues if i.severity == ValidationSeverity.ERROR])
        errors.extend([i for i in self.schema_issues if i.severity == ValidationSeverity.ERROR])
        return errors
    
    def get_all_warnings(self) -> List[ValidationIssue]:
        """Get all warnings from field and schema validation"""
        warnings = []
        for result in self.field_results.values():
            warnings.extend([i for i in result.issues if i.severity == ValidationSeverity.WARNING])
        warnings.extend([i for i in self.schema_issues if i.severity == ValidationSeverity.WARNING])
        return warnings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "product_id": self.product_id,
            "is_valid": self.is_valid,
            "score": round(self.score, 2),
            "timestamp": self.timestamp,
            "errors": [e.to_dict() for e in self.get_all_errors()],
            "warnings": [w.to_dict() for w in self.get_all_warnings()],
            "field_results": {name: result.to_dict() for name, result in self.field_results.items()},
            "schema_issues": [issue.to_dict() for issue in self.schema_issues],
            "error_count": len(self.get_all_errors()),
            "warning_count": len(self.get_all_warnings())
        }


@dataclass
class BatchValidationResult:
    """Result of batch validation"""
    total_products: int
    valid_products: int
    invalid_products: int
    product_results: List[ProductValidationResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_product_result(self, result: ProductValidationResult) -> None:
        """Add a product validation result"""
        self.product_results.append(result)
        if result.is_valid:
            self.valid_products += 1
        else:
            self.invalid_products += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_products": self.total_products,
            "valid_products": self.valid_products,
            "invalid_products": self.invalid_products,
            "success_rate": round(self.valid_products / self.total_products * 100, 2) if self.total_products > 0 else 0,
            "timestamp": self.timestamp,
            "product_results": [result.to_dict() for result in self.product_results]
        }


class FieldValidator:
    """Validates individual fields according to ChatGPT specification"""
    
    @staticmethod
    def validate_boolean(field_name: str, value: Any, constraints: Dict[str, Any]) -> FieldValidationResult:
        """Validate boolean field"""
        result = FieldValidationResult(field_name=field_name, is_valid=True, value=value)
        
        if not isinstance(value, bool):
            result.add_error(
                f"Field must be boolean, got {type(value).__name__}",
                suggestion="Use true or false",
                rule="type_check"
            )
        
        return result
    
    @staticmethod
    def validate_string(field_name: str, value: Any, constraints: Dict[str, Any]) -> FieldValidationResult:
        """Validate string field"""
        result = FieldValidationResult(field_name=field_name, is_valid=True, value=value)
        
        if not isinstance(value, str):
            result.add_error(
                f"Field must be string, got {type(value).__name__}",
                rule="type_check"
            )
            return result
        
        # Check not_empty
        if constraints.get('not_empty') and not value.strip():
            result.add_error("Field cannot be empty", rule="not_empty")
        
        # Check min_length
        min_length = constraints.get('min_length')
        if min_length and len(value) < min_length:
            result.add_error(
                f"Field must be at least {min_length} characters, got {len(value)}",
                suggestion=f"Add at least {min_length - len(value)} more characters",
                rule="min_length"
            )
        
        # Check max_length
        max_length = constraints.get('max_length')
        if max_length and len(value) > max_length:
            result.add_error(
                f"Field must not exceed {max_length} characters, got {len(value)}",
                suggestion=f"Remove at least {len(value) - max_length} characters",
                rule="max_length"
            )
        
        # Check pattern
        pattern = constraints.get('pattern')
        if pattern and not re.match(pattern, value):
            result.add_error(
                f"Field does not match required pattern: {pattern}",
                rule="pattern"
            )
        
        # Check enum
        enum_values = constraints.get('enum')
        if enum_values and value not in enum_values:
            result.add_error(
                f"Field must be one of: {', '.join(enum_values)}",
                suggestion=f"Use one of: {', '.join(enum_values)}",
                rule="enum"
            )
        
        return result
    
    @staticmethod
    def validate_number(field_name: str, value: Any, constraints: Dict[str, Any]) -> FieldValidationResult:
        """Validate number field"""
        result = FieldValidationResult(field_name=field_name, is_valid=True, value=value)
        
        if not isinstance(value, (int, float)):
            result.add_error(
                f"Field must be number, got {type(value).__name__}",
                rule="type_check"
            )
            return result
        
        # Check type (integer vs float)
        expected_type = constraints.get('type', 'float')
        if expected_type == 'integer' and not isinstance(value, int):
            result.add_error(
                "Field must be integer",
                suggestion="Remove decimal part",
                rule="integer_check"
            )
        
        # Check min
        min_value = constraints.get('min')
        if min_value is not None and value < min_value:
            result.add_error(
                f"Field must be at least {min_value}, got {value}",
                suggestion=f"Use value >= {min_value}",
                rule="min"
            )
        
        # Check max
        max_value = constraints.get('max')
        if max_value is not None and value > max_value:
            result.add_error(
                f"Field must not exceed {max_value}, got {value}",
                suggestion=f"Use value <= {max_value}",
                rule="max"
            )
        
        return result
    
    @staticmethod
    def validate_url(field_name: str, value: Any, constraints: Dict[str, Any]) -> FieldValidationResult:
        """Validate URL field"""
        result = FieldValidationResult(field_name=field_name, is_valid=True, value=value)
        
        if not isinstance(value, str):
            result.add_error(
                f"URL must be string, got {type(value).__name__}",
                rule="type_check"
            )
            return result
        
        # Check URL format
        if not value.startswith(('http://', 'https://')):
            result.add_error(
                "URL must start with http:// or https://",
                suggestion="Add protocol prefix (https://)",
                rule="url_format"
            )
        
        # Check max_length
        max_length = constraints.get('max_length', 2000)
        if len(value) > max_length:
            result.add_error(
                f"URL must not exceed {max_length} characters, got {len(value)}",
                rule="max_length"
            )
        
        # Check pattern if specified
        pattern = constraints.get('pattern')
        if pattern and not re.match(pattern, value, re.IGNORECASE):
            result.add_warning(
                f"URL may not match expected format",
                rule="pattern"
            )
        
        return result
    
    @staticmethod
    def validate_field(field_name: str, value: Any, field_type: str, constraints: Dict[str, Any]) -> FieldValidationResult:
        """Validate a field based on its type"""
        if field_type == 'boolean':
            return FieldValidator.validate_boolean(field_name, value, constraints)
        elif field_type == 'string':
            return FieldValidator.validate_string(field_name, value, constraints)
        elif field_type in ['number', 'integer', 'float']:
            return FieldValidator.validate_number(field_name, value, constraints)
        elif field_type == 'url':
            return FieldValidator.validate_url(field_name, value, constraints)
        elif field_type == 'enum':
            return FieldValidator.validate_string(field_name, value, constraints)
        else:
            # Generic validation
            result = FieldValidationResult(field_name=field_name, is_valid=True, value=value)
            return result


class ChatGPTSchemaValidator:
    """
    Comprehensive validator for ChatGPT product feed schema
    
    Validates products against ChatGPT specification with:
    - Field-level validation
    - Schema-level validation
    - Dependency checking
    - Detailed error reporting
    """
    
    def __init__(self):
        """Initialize validator with ChatGPT field specifications"""
        from chatgpt_feed_spec import ChatGPTFieldSpecification
        self.field_specs = ChatGPTFieldSpecification.get_field_specs()
        self.required_fields = ChatGPTFieldSpecification.get_required_fields()
        self.field_dependencies = ChatGPTFieldSpecification.get_field_dependencies()
    
    def validate_product(self, product_data: Dict[str, Any]) -> ProductValidationResult:
        """
        Validate a single product
        
        Args:
            product_data: Dictionary containing product data
            
        Returns:
            ProductValidationResult
        """
        product_id = product_data.get('id', 'unknown')
        result = ProductValidationResult(product_id=product_id, is_valid=True)
        
        # Check for required fields
        for field_name in self.required_fields:
            if field_name not in product_data:
                result.add_schema_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field_name=field_name,
                    message=f"Required field '{field_name}' is missing",
                    suggestion=f"Add '{field_name}' field to product data"
                ))
        
        # Validate each field present in product data
        for field_name, value in product_data.items():
            if field_name in self.field_specs:
                spec = self.field_specs[field_name]
                field_result = FieldValidator.validate_field(
                    field_name,
                    value,
                    spec.field_type,
                    spec.constraints
                )
                result.add_field_result(field_result)
            else:
                # Unknown field - add warning
                result.add_schema_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field_name=field_name,
                    message=f"Unknown field '{field_name}' (not in ChatGPT specification)",
                    value=value
                ))
        
        # Check field dependencies
        for field_name, dependencies in self.field_dependencies.items():
            if field_name in product_data:
                for dep_field in dependencies:
                    if dep_field not in product_data:
                        result.add_schema_issue(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            field_name=field_name,
                            message=f"Field '{field_name}' requires '{dep_field}' to be present",
                            suggestion=f"Add '{dep_field}' field"
                        ))
                    # Check enable_checkout dependency on enable_search
                    elif field_name == 'enable_checkout' and dep_field == 'enable_search':
                        if product_data.get('enable_checkout') and not product_data.get('enable_search'):
                            result.add_schema_issue(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                field_name=field_name,
                                message="enable_checkout requires enable_search to be true",
                                suggestion="Set enable_search to true or disable enable_checkout"
                            ))
        
        # Calculate validation score (0-100)
        result.score = self._calculate_score(result)
        
        return result
    
    def validate_batch(self, products: List[Dict[str, Any]]) -> BatchValidationResult:
        """
        Validate multiple products
        
        Args:
            products: List of product data dictionaries
            
        Returns:
            BatchValidationResult
        """
        batch_result = BatchValidationResult(
            total_products=len(products),
            valid_products=0,
            invalid_products=0
        )
        
        for product_data in products:
            product_result = self.validate_product(product_data)
            batch_result.add_product_result(product_result)
        
        return batch_result
    
    def generate_report(self, result: Union[ProductValidationResult, BatchValidationResult]) -> str:
        """
        Generate a human-readable validation report
        
        Args:
            result: Validation result (product or batch)
            
        Returns:
            Formatted report string
        """
        lines = []
        
        if isinstance(result, ProductValidationResult):
            lines.append("=" * 80)
            lines.append(f"Product Validation Report: {result.product_id}")
            lines.append("=" * 80)
            lines.append(f"Status: {'VALID' if result.is_valid else 'INVALID'}")
            lines.append(f"Score: {result.score}/100")
            lines.append(f"Timestamp: {result.timestamp}")
            
            errors = result.get_all_errors()
            warnings = result.get_all_warnings()
            
            if errors:
                lines.append(f"\nErrors ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    lines.append(f"  {i}. [{error.field_name}] {error.message}")
                    if error.suggestion:
                        lines.append(f"     Suggestion: {error.suggestion}")
            
            if warnings:
                lines.append(f"\nWarnings ({len(warnings)}):")
                for i, warning in enumerate(warnings, 1):
                    lines.append(f"  {i}. [{warning.field_name}] {warning.message}")
                    if warning.suggestion:
                        lines.append(f"     Suggestion: {warning.suggestion}")
            
            if not errors and not warnings:
                lines.append("\nNo issues found!")
        
        elif isinstance(result, BatchValidationResult):
            lines.append("=" * 80)
            lines.append("Batch Validation Report")
            lines.append("=" * 80)
            lines.append(f"Total Products: {result.total_products}")
            lines.append(f"Valid Products: {result.valid_products}")
            lines.append(f"Invalid Products: {result.invalid_products}")
            lines.append(f"Success Rate: {result.to_dict()['success_rate']}%")
            lines.append(f"Timestamp: {result.timestamp}")
            
            if result.invalid_products > 0:
                lines.append(f"\nInvalid Products:")
                for i, prod_result in enumerate(result.product_results, 1):
                    if not prod_result.is_valid:
                        error_count = len(prod_result.get_all_errors())
                        lines.append(f"  {i}. Product {prod_result.product_id}: {error_count} errors")
        
        return "\n".join(lines)
    
    def _calculate_score(self, result: ProductValidationResult) -> float:
        """
        Calculate validation score (0-100) based on errors and warnings
        
        Args:
            result: ProductValidationResult
            
        Returns:
            Score from 0 to 100
        """
        score = 100.0
        errors = result.get_all_errors()
        warnings = result.get_all_warnings()
        
        # Deduct points for errors (more severe)
        score -= len(errors) * 10
        
        # Deduct points for warnings (less severe)
        score -= len(warnings) * 2
        
        # Ensure score is not negative
        score = max(0.0, score)
        
        return score


def validate_product_example():
    """Example usage of product validation"""
    
    # Valid product example
    valid_product = {
        "enable_search": True,
        "enable_checkout": True,
        "id": "PROD001",
        "title": "Wireless Bluetooth Headphones",
        "description": "High-quality wireless headphones with active noise cancellation and 30-hour battery life.",
        "price": 99.99,
        "currency": "USD",
        "availability": "in_stock",
        "image_link": "https://example.com/headphones.jpg",
        "link": "https://example.com/products/headphones",
        "category": "Electronics",
        "brand": "AudioTech",
        "rating": 4.5,
        "reviews_count": 250
    }
    
    # Invalid product example
    invalid_product = {
        "enable_search": False,
        "enable_checkout": True,  # Error: requires enable_search=True
        "id": "",  # Error: empty
        "title": "USB Cable",
        "description": "Short",  # Error: too short
        "price": -10,  # Error: negative
        "currency": "US",  # Error: invalid format
        "availability": "available",  # Error: invalid enum value
        "image_link": "not-a-url",  # Error: invalid URL
        "link": "example.com/product"  # Error: missing protocol
    }
    
    validator = ChatGPTSchemaValidator()
    
    print("Validating valid product:")
    valid_result = validator.validate_product(valid_product)
    print(validator.generate_report(valid_result))
    
    print("\n" + "=" * 80 + "\n")
    
    print("Validating invalid product:")
    invalid_result = validator.validate_product(invalid_product)
    print(validator.generate_report(invalid_result))
    
    # Print JSON report
    print("\n" + "=" * 80 + "\n")
    print("JSON Report:")
    print(json.dumps(invalid_result.to_dict(), indent=2))


def validate_batch_example():
    """Example usage of batch validation"""
    
    products = [
        {
            "enable_search": True,
            "enable_checkout": True,
            "id": "PROD001",
            "title": "Product 1",
            "description": "Description for product 1 with sufficient length",
            "price": 29.99,
            "currency": "USD",
            "availability": "in_stock",
            "image_link": "https://example.com/p1.jpg",
            "link": "https://example.com/p1"
        },
        {
            "enable_search": True,
            "enable_checkout": True,
            "id": "PROD002",
            "title": "Product 2",
            "description": "Description for product 2 with sufficient length",
            "price": 49.99,
            "currency": "USD",
            "availability": "in_stock",
            "image_link": "https://example.com/p2.jpg",
            "link": "https://example.com/p2"
        },
        {
            # Invalid product - missing required fields
            "id": "PROD003",
            "title": "Product 3"
        }
    ]
    
    validator = ChatGPTSchemaValidator()
    batch_result = validator.validate_batch(products)
    
    print("Batch Validation Report:")
    print(validator.generate_report(batch_result))
    
    print("\n" + "=" * 80 + "\n")
    print("JSON Report:")
    print(json.dumps(batch_result.to_dict(), indent=2))


if __name__ == "__main__":
    print("ChatGPT Schema Validator Examples\n")
    validate_product_example()
    print("\n" + "=" * 80 + "\n")
    validate_batch_example()
