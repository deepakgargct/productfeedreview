"""
ChatGPT Product Feed Validator

A comprehensive product feed validation module that validates product data
against ChatGPT best practices and marketplace standards. Includes schema
validation, content quality checks, and automated recommendations.

Author: deepakgargct
Date: 2026-01-06
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ProductCategory(Enum):
    """Supported product categories"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME_GARDEN = "home_and_garden"
    SPORTS = "sports"
    BOOKS = "books"
    FOOD = "food"
    BEAUTY = "beauty"
    TOYS = "toys"
    OTHER = "other"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    level: ValidationLevel
    field: str
    message: str
    suggestion: Optional[str] = None
    value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "level": self.level.value,
            "field": self.field,
            "message": self.message,
            "suggestion": self.suggestion,
            "value": self.value
        }


@dataclass
class ValidationResult:
    """Comprehensive validation result"""
    is_valid: bool
    product_id: str
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue"""
        if issue.level == ValidationLevel.ERROR:
            self.issues.append(issue)
        elif issue.level == ValidationLevel.WARNING:
            self.warnings.append(issue)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "product_id": self.product_id,
            "score": round(self.score, 2),
            "errors": [issue.to_dict() for issue in self.issues],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "error_count": len(self.issues),
            "warning_count": len(self.warnings),
            "timestamp": self.timestamp
        }


class ChatGPTFeedValidator:
    """
    Comprehensive product feed validator for ChatGPT compliance
    """

    # Validation constraints
    MIN_TITLE_LENGTH = 10
    MAX_TITLE_LENGTH = 150
    MIN_DESCRIPTION_LENGTH = 20
    MAX_DESCRIPTION_LENGTH = 5000
    MIN_PRICE = 0.01
    MAX_PRICE = 999999.99
    MIN_RATING = 0.0
    MAX_RATING = 5.0

    # Required fields
    REQUIRED_FIELDS = {
        'product_id', 'title', 'description', 'price',
        'currency', 'category', 'availability'
    }

    # Optional but recommended fields
    RECOMMENDED_FIELDS = {
        'image_url', 'product_url', 'rating', 'review_count',
        'manufacturer', 'sku', 'stock_quantity'
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator

        Args:
            strict_mode: If True, enforce stricter validation rules
        """
        self.strict_mode = strict_mode
        self.validation_results: List[ValidationResult] = []

    def validate_product(self, product: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single product

        Args:
            product: Product data dictionary

        Returns:
            ValidationResult object
        """
        product_id = product.get('product_id', 'UNKNOWN')
        result = ValidationResult(is_valid=True, product_id=product_id)

        # Check required fields
        self._validate_required_fields(product, result)

        # Validate individual fields
        if result.is_valid or not self.strict_mode:
            self._validate_title(product.get('title'), result)
            self._validate_description(product.get('description'), result)
            self._validate_price(product.get('price'), result)
            self._validate_currency(product.get('currency'), result)
            self._validate_category(product.get('category'), result)
            self._validate_availability(product.get('availability'), result)
            self._validate_optional_fields(product, result)

        # Calculate quality score
        self._calculate_score(result, product)

        # Update validity based on errors
        result.is_valid = len(result.issues) == 0

        self.validation_results.append(result)
        return result

    def validate_feed(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate entire product feed

        Args:
            products: List of product dictionaries

        Returns:
            Feed validation summary
        """
        if not products:
            logger.warning("Empty product feed provided")
            return {
                "total_products": 0,
                "valid_products": 0,
                "invalid_products": 0,
                "average_score": 0,
                "products": []
            }

        self.validation_results = []
        for product in products:
            self.validate_product(product)

        return self._generate_feed_report()

    def _validate_required_fields(
        self, product: Dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate required fields presence"""
        missing_fields = self.REQUIRED_FIELDS - set(product.keys())

        if missing_fields:
            result.is_valid = False
            for field in missing_fields:
                issue = ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field=field,
                    message=f"Required field '{field}' is missing",
                    suggestion=f"Please provide a valid value for '{field}'"
                )
                result.add_issue(issue)

    def _validate_title(self, title: Optional[str], result: ValidationResult) -> None:
        """Validate product title"""
        if not title:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='title',
                message="Product title is missing or empty",
                suggestion="Provide a clear, descriptive title (10-150 characters)"
            ))
            return

        title = str(title).strip()

        # Length validation
        if len(title) < self.MIN_TITLE_LENGTH:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='title',
                message=f"Title is too short (minimum {self.MIN_TITLE_LENGTH} characters)",
                suggestion="Provide more descriptive product name",
                value=title
            ))

        if len(title) > self.MAX_TITLE_LENGTH:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='title',
                message=f"Title exceeds recommended length ({self.MAX_TITLE_LENGTH} characters)",
                suggestion="Shorten the title for better readability",
                value=title
            ))

        # Content quality
        if self._contains_excessive_keywords(title):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='title',
                message="Title contains excessive keywords or repetition",
                suggestion="Use natural language without keyword stuffing",
                value=title
            ))

        if self._contains_special_characters(title):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='title',
                message="Title contains unusual special characters",
                suggestion="Keep special characters minimal in titles",
                value=title
            ))

    def _validate_description(
        self, description: Optional[str], result: ValidationResult
    ) -> None:
        """Validate product description"""
        if not description:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='description',
                message="Product description is missing or empty",
                suggestion="Provide detailed product description (20-5000 characters)"
            ))
            return

        description = str(description).strip()

        # Length validation
        if len(description) < self.MIN_DESCRIPTION_LENGTH:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='description',
                message=f"Description too short (minimum {self.MIN_DESCRIPTION_LENGTH} characters)",
                suggestion="Provide more comprehensive product details",
                value=description[:50]
            ))

        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='description',
                message=f"Description exceeds recommended length ({self.MAX_DESCRIPTION_LENGTH} characters)",
                suggestion="Condense description while retaining key information",
                value=description[:50]
            ))

        # Content quality
        if self._contains_html_tags(description):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='description',
                message="Description contains HTML tags",
                suggestion="Remove or escape HTML tags for plain text compatibility"
            ))

        if self._is_low_quality_content(description):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='description',
                message="Description quality appears low",
                suggestion="Provide informative, clear description with proper grammar"
            ))

    def _validate_price(self, price: Optional[Any], result: ValidationResult) -> None:
        """Validate product price"""
        if price is None or price == '':
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='price',
                message="Price is missing",
                suggestion="Provide a valid product price as a number"
            ))
            return

        try:
            price_float = float(price)
        except (ValueError, TypeError):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='price',
                message=f"Price is not a valid number: {price}",
                suggestion="Provide price as a numeric value",
                value=price
            ))
            return

        # Range validation
        if price_float < self.MIN_PRICE:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='price',
                message=f"Price is below minimum ({self.MIN_PRICE})",
                suggestion="Ensure price is greater than zero",
                value=price_float
            ))

        if price_float > self.MAX_PRICE:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='price',
                message=f"Price exceeds typical range ({self.MAX_PRICE})",
                suggestion="Verify price is correct",
                value=price_float
            ))

    def _validate_currency(self, currency: Optional[str], result: ValidationResult) -> None:
        """Validate currency code"""
        if not currency:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='currency',
                message="Currency is missing",
                suggestion="Provide a valid ISO 4217 currency code (e.g., USD, EUR, GBP)"
            ))
            return

        currency = str(currency).upper().strip()

        # Valid currency codes
        valid_currencies = {
            'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY',
            'INR', 'MXN', 'BRL', 'ZAR', 'SGD', 'HKD', 'NZD', 'SEK',
            'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RON', 'BGN', 'HRK'
        }

        if currency not in valid_currencies:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='currency',
                message=f"Currency code '{currency}' may be invalid",
                suggestion="Use standard ISO 4217 currency codes",
                value=currency
            ))

    def _validate_category(self, category: Optional[str], result: ValidationResult) -> None:
        """Validate product category"""
        if not category:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='category',
                message="Product category is missing",
                suggestion=f"Provide a valid category from: {', '.join([c.value for c in ProductCategory])}"
            ))
            return

        category = str(category).lower().strip()
        valid_categories = [c.value for c in ProductCategory]

        if category not in valid_categories:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='category',
                message=f"Category '{category}' not in standard list",
                suggestion=f"Use standard categories: {', '.join(valid_categories)}",
                value=category
            ))

    def _validate_availability(
        self, availability: Optional[str], result: ValidationResult
    ) -> None:
        """Validate product availability"""
        if not availability:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                field='availability',
                message="Availability status is missing",
                suggestion="Specify availability: 'in_stock', 'out_of_stock', or 'preorder'"
            ))
            return

        availability = str(availability).lower().strip()
        valid_statuses = {'in_stock', 'out_of_stock', 'preorder', 'available', 'unavailable'}

        if availability not in valid_statuses:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='availability',
                message=f"Availability status '{availability}' not standard",
                suggestion="Use: 'in_stock', 'out_of_stock', or 'preorder'",
                value=availability
            ))

    def _validate_optional_fields(
        self, product: Dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate optional but recommended fields"""
        # Image URL validation
        if 'image_url' in product:
            self._validate_url(product['image_url'], 'image_url', result)
        else:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.INFO,
                field='image_url',
                message="Product image URL is recommended but missing",
                suggestion="Add high-quality product image URL for better visibility"
            ))

        # Product URL validation
        if 'product_url' in product:
            self._validate_url(product['product_url'], 'product_url', result)
        else:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.INFO,
                field='product_url',
                message="Product URL is recommended but missing",
                suggestion="Provide link to product landing page"
            ))

        # Rating validation
        if 'rating' in product:
            self._validate_rating(product['rating'], result)

        # Stock quantity validation
        if 'stock_quantity' in product:
            self._validate_stock_quantity(product['stock_quantity'], result)

    def _validate_url(
        self, url: Optional[str], field_name: str, result: ValidationResult
    ) -> None:
        """Validate URL format"""
        if not url:
            return

        url = str(url).strip()
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field=field_name,
                message=f"Invalid URL format for {field_name}",
                suggestion="Ensure URL starts with http:// or https://",
                value=url
            ))

    def _validate_rating(self, rating: Optional[Any], result: ValidationResult) -> None:
        """Validate product rating"""
        if rating is None or rating == '':
            return

        try:
            rating_float = float(rating)
        except (ValueError, TypeError):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='rating',
                message=f"Rating is not a valid number: {rating}",
                suggestion="Provide rating as a number between 0 and 5",
                value=rating
            ))
            return

        if rating_float < self.MIN_RATING or rating_float > self.MAX_RATING:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='rating',
                message=f"Rating out of valid range (0-5): {rating_float}",
                suggestion="Ensure rating is between 0 and 5 stars",
                value=rating_float
            ))

    def _validate_stock_quantity(
        self, quantity: Optional[Any], result: ValidationResult
    ) -> None:
        """Validate stock quantity"""
        if quantity is None or quantity == '':
            return

        try:
            quantity_int = int(quantity)
        except (ValueError, TypeError):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='stock_quantity',
                message=f"Stock quantity is not a valid integer: {quantity}",
                suggestion="Provide stock quantity as a whole number",
                value=quantity
            ))
            return

        if quantity_int < 0:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                field='stock_quantity',
                message="Stock quantity cannot be negative",
                suggestion="Use 0 for out of stock items",
                value=quantity_int
            ))

    @staticmethod
    def _contains_excessive_keywords(text: str) -> bool:
        """Check for keyword stuffing"""
        words = text.split()
        if len(words) == 0:
            return False
        word_freq = {}
        for word in words:
            word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
        # Flag if any word appears more than 3 times
        return any(count > 3 for count in word_freq.values())

    @staticmethod
    def _contains_special_characters(text: str) -> bool:
        """Check for excessive special characters"""
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s\-&/]', text))
        return special_chars > len(text) * 0.1  # More than 10% special chars

    @staticmethod
    def _contains_html_tags(text: str) -> bool:
        """Check for HTML tags"""
        return bool(re.search(r'<[^>]+>', text))

    @staticmethod
    def _is_low_quality_content(text: str) -> bool:
        """Assess content quality"""
        # Check for very short sentences
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # Check for repeated words
        words = text.lower().split()
        unique_ratio = len(set(words)) / max(len(words), 1)

        return avg_sentence_length < 3 or unique_ratio < 0.5

    def _calculate_score(
        self, result: ValidationResult, product: Dict[str, Any]
    ) -> None:
        """Calculate product quality score"""
        max_score = 100.0
        deductions = 0.0

        # Deduct for errors
        deductions += len(result.issues) * 10

        # Deduct for warnings
        deductions += len(result.warnings) * 3

        # Deduct for missing recommended fields
        missing_recommended = self.RECOMMENDED_FIELDS - set(product.keys())
        deductions += len(missing_recommended) * 2

        result.score = max(0.0, max_score - deductions)

    def _generate_feed_report(self) -> Dict[str, Any]:
        """Generate comprehensive feed validation report"""
        valid_count = sum(1 for r in self.validation_results if r.is_valid)
        invalid_count = len(self.validation_results) - valid_count
        avg_score = sum(r.score for r in self.validation_results) / max(
            len(self.validation_results), 1
        )

        return {
            "total_products": len(self.validation_results),
            "valid_products": valid_count,
            "invalid_products": invalid_count,
            "validity_percentage": round((valid_count / max(len(self.validation_results), 1)) * 100, 2),
            "average_score": round(avg_score, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "products": [r.to_dict() for r in self.validation_results]
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        if not self.validation_results:
            return {"message": "No validation results available"}

        return {
            "total_validations": len(self.validation_results),
            "passed": sum(1 for r in self.validation_results if r.is_valid),
            "failed": sum(1 for r in self.validation_results if not r.is_valid),
            "average_score": round(sum(r.score for r in self.validation_results) / len(self.validation_results), 2),
            "total_errors": sum(len(r.issues) for r in self.validation_results),
            "total_warnings": sum(len(r.warnings) for r in self.validation_results)
        }

    def export_results(self, format_type: str = 'json') -> str:
        """
        Export validation results in specified format

        Args:
            format_type: 'json' or 'csv'

        Returns:
            Formatted results string
        """
        if format_type.lower() == 'json':
            return json.dumps(self._generate_feed_report(), indent=2)
        elif format_type.lower() == 'csv':
            return self._export_as_csv()
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _export_as_csv(self) -> str:
        """Export results as CSV"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Product ID', 'Valid', 'Score', 'Errors', 'Warnings', 'Issues'
        ])

        # Rows
        for result in self.validation_results:
            issues_str = '; '.join([
                f"{i.field}: {i.message}" for i in result.issues + result.warnings
            ])
            writer.writerow([
                result.product_id,
                'Yes' if result.is_valid else 'No',
                result.score,
                len(result.issues),
                len(result.warnings),
                issues_str
            ])

        return output.getvalue()


# Example usage and testing
if __name__ == "__main__":
    # Sample product data
    sample_products = [
        {
            "product_id": "PROD001",
            "title": "Premium Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation, 30-hour battery life, and premium sound quality. Perfect for music lovers and professionals.",
            "price": 149.99,
            "currency": "USD",
            "category": "electronics",
            "availability": "in_stock",
            "image_url": "https://example.com/images/headphones.jpg",
            "product_url": "https://example.com/products/headphones",
            "rating": 4.5,
            "review_count": 1250,
            "stock_quantity": 150
        },
        {
            "product_id": "PROD002",
            "title": "Short",  # Too short
            "description": "Product",  # Too short
            "price": -50,  # Invalid price
            "currency": "INVALID",  # Invalid currency
            "category": "unknown",  # Invalid category
            "availability": "maybe"  # Invalid availability
        },
        {
            "product_id": "PROD003",
            "title": "Organic Cotton T-Shirt",
            "description": "Comfortable and eco-friendly organic cotton t-shirt perfect for everyday wear.",
            "price": 29.99,
            "currency": "EUR",
            "category": "clothing",
            "availability": "in_stock",
            "rating": 4.8
        }
    ]

    # Validate products
    validator = ChatGPTFeedValidator(strict_mode=False)
    feed_report = validator.validate_feed(sample_products)

    print("Feed Validation Report:")
    print(json.dumps(feed_report, indent=2))

    print("\n" + "="*50)
    print("Validation Summary:")
    print(json.dumps(validator.get_summary(), indent=2))
