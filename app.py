"""
Product Feed Review Application
Integrated ChatGPT Product Feed Specification with comprehensive validation and recommendations
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class FieldType(Enum):
    """Field type classifications"""
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class ChatGPTSchemaValidator:
    """
    Comprehensive validator for ChatGPT Product Feed Specification
    Validates required, recommended, and optional fields with intelligent recommendations
    """

    # ChatGPT Product Feed Schema Specification
    SCHEMA = {
        # Required Fields - Must be present for valid feed
        "required_fields": {
            "id": {
                "type": "string",
                "description": "Unique product identifier",
                "validation": "non-empty string, max 100 chars",
                "examples": ["SKU-12345", "PRODUCT-001"]
            },
            "title": {
                "type": "string",
                "description": "Product title/name",
                "validation": "non-empty string, max 150 chars, no HTML",
                "examples": ["Premium Wireless Headphones", "Organic Coffee Beans"]
            },
            "description": {
                "type": "string",
                "description": "Detailed product description",
                "validation": "non-empty string, max 5000 chars",
                "examples": ["High-quality audio with noise cancellation..."]
            },
            "price": {
                "type": "number",
                "description": "Product price in specified currency",
                "validation": "positive number with up to 2 decimal places",
                "examples": ["29.99", "1500.00"]
            },
            "currency": {
                "type": "string",
                "description": "Currency code (ISO 4217)",
                "validation": "3-letter currency code",
                "examples": ["USD", "EUR", "GBP"]
            },
            "availability": {
                "type": "string",
                "description": "Stock availability status",
                "validation": "in_stock | out_of_stock | preorder",
                "examples": ["in_stock", "preorder"]
            },
            "product_url": {
                "type": "string",
                "description": "Direct link to product page",
                "validation": "valid URL format",
                "examples": ["https://example.com/product/123"]
            },
            "image_url": {
                "type": "string",
                "description": "Primary product image URL",
                "validation": "valid URL, preferably 1200x1200 or larger",
                "examples": ["https://example.com/images/product-123.jpg"]
            }
        },

        # Recommended Fields - Highly recommended for better visibility and conversion
        "recommended_fields": {
            "category": {
                "type": "string",
                "description": "Product category/classification",
                "validation": "categorized in standard taxonomy",
                "examples": ["Electronics > Audio", "Home > Kitchen"],
                "impact": "Improves search filtering and discovery"
            },
            "brand": {
                "type": "string",
                "description": "Brand or manufacturer name",
                "validation": "non-empty string, max 100 chars",
                "examples": ["Sony", "Apple", "Samsung"],
                "impact": "Enables brand-based filtering and trust signals"
            },
            "sku": {
                "type": "string",
                "description": "Stock Keeping Unit",
                "validation": "unique identifier, alphanumeric",
                "examples": ["WH-1000XM4", "IPHONE-13-BLK"],
                "impact": "Better inventory tracking and variant management"
            },
            "quantity": {
                "type": "integer",
                "description": "Quantity available in stock",
                "validation": "non-negative integer",
                "examples": ["100", "0", "500"],
                "impact": "Real-time stock level visibility"
            },
            "sale_price": {
                "type": "number",
                "description": "Discounted price if on sale",
                "validation": "positive number, less than regular price",
                "examples": ["24.99", "899.00"],
                "impact": "Highlights deals and promotions"
            },
            "condition": {
                "type": "string",
                "description": "Product condition",
                "validation": "new | refurbished | used",
                "examples": ["new", "refurbished"],
                "impact": "Sets buyer expectations and trust"
            },
            "rating": {
                "type": "number",
                "description": "Average product rating",
                "validation": "number between 0 and 5, max 1 decimal",
                "examples": ["4.5", "3.8"],
                "impact": "Social proof and conversion optimization"
            },
            "review_count": {
                "type": "integer",
                "description": "Number of customer reviews",
                "validation": "non-negative integer",
                "examples": ["150", "1000"],
                "impact": "Credibility and review volume signal"
            },
            "additional_images": {
                "type": "array",
                "description": "Alternative product images",
                "validation": "array of valid URLs",
                "examples": ["URL1, URL2, URL3"],
                "impact": "Enhanced visual presentation"
            },
            "attributes": {
                "type": "object",
                "description": "Key-value product attributes",
                "validation": "JSON object with relevant specs",
                "examples": ["color: blue, size: large, material: cotton"],
                "impact": "Detailed product specification visibility"
            },
            "shipping_cost": {
                "type": "number",
                "description": "Shipping cost",
                "validation": "non-negative number",
                "examples": ["5.99", "0"],
                "impact": "Total cost transparency"
            },
            "shipping_weight": {
                "type": "number",
                "description": "Product weight in kg",
                "validation": "positive number",
                "examples": ["2.5", "0.5"],
                "impact": "Shipping cost estimation accuracy"
            }
        },

        # Optional Fields - Nice to have for enhanced features
        "optional_fields": {
            "color": {
                "type": "string",
                "description": "Product color variant",
                "examples": ["Black", "Blue", "Rose Gold"]
            },
            "size": {
                "type": "string",
                "description": "Product size",
                "examples": ["Large", "XL", "10ft"]
            },
            "material": {
                "type": "string",
                "description": "Primary material composition",
                "examples": ["Aluminum", "Leather", "Cotton"]
            },
            "dimensions": {
                "type": "string",
                "description": "Product dimensions (L x W x H)",
                "examples": ["10cm x 5cm x 3cm"]
            },
            "warranty_months": {
                "type": "integer",
                "description": "Warranty duration in months",
                "examples": ["12", "24"]
            },
            "upc": {
                "type": "string",
                "description": "Universal Product Code",
                "examples": ["012345678905"]
            },
            "ean": {
                "type": "string",
                "description": "European Article Number",
                "examples": ["5901234123457"]
            },
            "manufacturer": {
                "type": "string",
                "description": "Manufacturer name",
                "examples": ["Sony Corporation", "Samsung Electronics"]
            },
            "supplier": {
                "type": "string",
                "description": "Product supplier/distributor",
                "examples": ["XYZ Distributors"]
            },
            "keywords": {
                "type": "array",
                "description": "SEO keywords for discoverability",
                "examples": ["wireless, headphones, noise-cancelling"]
            },
            "tags": {
                "type": "array",
                "description": "Product tags for categorization",
                "examples": ["bestseller, new-arrival, eco-friendly"]
            },
            "expiration_date": {
                "type": "string",
                "description": "Product expiration date (YYYY-MM-DD)",
                "examples": ["2026-12-31"]
            },
            "last_updated": {
                "type": "string",
                "description": "Last modification timestamp",
                "examples": ["2026-01-06T12:39:38Z"]
            },
            "gtin": {
                "type": "string",
                "description": "Global Trade Item Number",
                "examples": ["01234567890128"]
            }
        }
    }

    def __init__(self):
        """Initialize validator with schema"""
        self.schema = self.SCHEMA
        self.validation_results = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "recommendations": [],
            "field_analysis": {},
            "score": 0
        }

    def validate_product(self, product_data: Dict) -> Dict:
        """
        Validate complete product against ChatGPT specification
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Dictionary with validation results, recommendations, and analysis
        """
        self.validation_results = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "recommendations": [],
            "field_analysis": {},
            "score": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Validate required fields
        self._validate_required_fields(product_data)

        # Validate recommended fields
        self._validate_recommended_fields(product_data)

        # Validate optional fields
        self._validate_optional_fields(product_data)

        # Generate intelligent recommendations
        self._generate_recommendations(product_data)

        # Calculate completeness score
        self._calculate_score(product_data)

        # Set validity status
        self.validation_results["valid"] = len(self.validation_results["errors"]) == 0

        return self.validation_results

    def _validate_required_fields(self, product_data: Dict) -> None:
        """Validate all required fields"""
        required = self.schema["required_fields"]
        
        for field_name, field_spec in required.items():
            analysis = {
                "type": FieldType.REQUIRED.value,
                "present": field_name in product_data,
                "value": product_data.get(field_name),
                "specification": field_spec,
                "issues": []
            }

            if field_name not in product_data:
                error_msg = f"Required field '{field_name}' is missing. {field_spec['description']}"
                self.validation_results["errors"].append({
                    "field": field_name,
                    "type": FieldType.REQUIRED.value,
                    "message": error_msg
                })
                analysis["issues"].append("Missing required field")
            else:
                # Validate field content
                field_issues = self._validate_field_content(
                    field_name, 
                    product_data[field_name], 
                    field_spec
                )
                if field_issues:
                    analysis["issues"].extend(field_issues)
                    for issue in field_issues:
                        self.validation_results["errors"].append({
                            "field": field_name,
                            "type": FieldType.REQUIRED.value,
                            "message": issue
                        })

            self.validation_results["field_analysis"][field_name] = analysis

    def _validate_recommended_fields(self, product_data: Dict) -> None:
        """Validate recommended fields and flag missing ones"""
        recommended = self.schema["recommended_fields"]
        
        for field_name, field_spec in recommended.items():
            analysis = {
                "type": FieldType.RECOMMENDED.value,
                "present": field_name in product_data,
                "value": product_data.get(field_name),
                "specification": field_spec,
                "impact": field_spec.get("impact", ""),
                "issues": []
            }

            if field_name not in product_data:
                warning_msg = f"Recommended field '{field_name}' is missing. {field_spec['description']}. Impact: {field_spec.get('impact', 'N/A')}"
                self.validation_results["warnings"].append({
                    "field": field_name,
                    "type": FieldType.RECOMMENDED.value,
                    "message": warning_msg
                })
            else:
                # Validate field content
                field_issues = self._validate_field_content(
                    field_name,
                    product_data[field_name],
                    field_spec
                )
                if field_issues:
                    analysis["issues"].extend(field_issues)
                    for issue in field_issues:
                        self.validation_results["warnings"].append({
                            "field": field_name,
                            "type": FieldType.RECOMMENDED.value,
                            "message": issue
                        })

            self.validation_results["field_analysis"][field_name] = analysis

    def _validate_optional_fields(self, product_data: Dict) -> None:
        """Validate optional fields when present"""
        optional = self.schema["optional_fields"]
        
        for field_name, field_spec in optional.items():
            if field_name in product_data:
                analysis = {
                    "type": FieldType.OPTIONAL.value,
                    "present": True,
                    "value": product_data.get(field_name),
                    "specification": field_spec,
                    "issues": []
                }

                # Validate field content
                field_issues = self._validate_field_content(
                    field_name,
                    product_data[field_name],
                    field_spec
                )
                if field_issues:
                    analysis["issues"].extend(field_issues)

                self.validation_results["field_analysis"][field_name] = analysis

    def _validate_field_content(self, field_name: str, value: Any, field_spec: Dict) -> List[str]:
        """
        Validate specific field content based on type and rules
        
        Args:
            field_name: Name of the field
            value: Field value to validate
            field_spec: Field specification
            
        Returns:
            List of validation issues found
        """
        issues = []
        field_type = field_spec.get("type", "string")

        # Type validation
        if field_type == "string":
            if not isinstance(value, str) or len(value.strip()) == 0:
                issues.append(f"'{field_name}' must be a non-empty string")
        elif field_type == "number":
            try:
                float(value)
            except (TypeError, ValueError):
                issues.append(f"'{field_name}' must be a valid number")
        elif field_type == "integer":
            try:
                int(value)
            except (TypeError, ValueError):
                issues.append(f"'{field_name}' must be a valid integer")
        elif field_type == "array":
            if not isinstance(value, (list, str)):
                issues.append(f"'{field_name}' must be an array or comma-separated string")
        elif field_type == "object":
            if not isinstance(value, dict):
                issues.append(f"'{field_name}' must be a valid object/dictionary")

        # Field-specific validation
        if field_name == "price":
            try:
                price = float(value)
                if price < 0:
                    issues.append("Price must be a positive number")
                if price > 0 and len(str(value).split('.')[-1]) > 2:
                    issues.append("Price should have maximum 2 decimal places")
            except:
                pass

        elif field_name == "rating":
            try:
                rating = float(value)
                if rating < 0 or rating > 5:
                    issues.append("Rating must be between 0 and 5")
            except:
                pass

        elif field_name == "product_url" or field_name == "image_url":
            if not self._is_valid_url(str(value)):
                issues.append(f"'{field_name}' must be a valid URL")

        elif field_name == "currency":
            if len(str(value)) != 3 or not str(value).isupper():
                issues.append("Currency must be a 3-letter ISO 4217 code (e.g., USD)")

        elif field_name == "availability":
            valid_values = ["in_stock", "out_of_stock", "preorder"]
            if str(value).lower() not in valid_values:
                issues.append(f"Availability must be one of: {', '.join(valid_values)}")

        elif field_name == "condition":
            valid_values = ["new", "refurbished", "used"]
            if str(value).lower() not in valid_values:
                issues.append(f"Condition must be one of: {', '.join(valid_values)}")

        return issues

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    def _generate_recommendations(self, product_data: Dict) -> None:
        """Generate intelligent recommendations for improving the feed"""
        recommendations = []

        # Check for missing recommended fields
        recommended = self.schema["recommended_fields"]
        missing_recommended = [
            field for field in recommended.keys() 
            if field not in product_data
        ]

        if missing_recommended:
            recommendations.append({
                "priority": "high",
                "category": "Missing Recommended Fields",
                "fields": missing_recommended,
                "message": f"Add {len(missing_recommended)} recommended fields to improve product visibility and conversion rates",
                "action": "Include brand, category, rating, and review_count for better search performance"
            })

        # Price recommendations
        if "sale_price" not in product_data and "price" in product_data:
            try:
                price = float(product_data["price"])
                recommendations.append({
                    "priority": "medium",
                    "category": "Pricing Strategy",
                    "fields": ["sale_price"],
                    "message": "Consider adding a sale_price to highlight discounts",
                    "action": "If product is on promotion, add sale_price field"
                })
            except:
                pass

        # Rating recommendations
        if "rating" not in product_data or "review_count" not in product_data:
            recommendations.append({
                "priority": "high",
                "category": "Social Proof",
                "fields": ["rating", "review_count"],
                "message": "Add ratings and review counts to build customer trust",
                "action": "Include customer ratings and number of reviews for credibility"
            })

        # Image recommendations
        if "image_url" in product_data and "additional_images" not in product_data:
            recommendations.append({
                "priority": "medium",
                "category": "Visual Content",
                "fields": ["additional_images"],
                "message": "Add multiple product images for better visual presentation",
                "action": "Include at least 3-5 additional images from different angles"
            })

        # Attribute recommendations
        if "attributes" not in product_data:
            recommendations.append({
                "priority": "medium",
                "category": "Product Details",
                "fields": ["attributes"],
                "message": "Add detailed product attributes for enhanced specifications",
                "action": "Include color, size, material, dimensions, and other relevant specs"
            })

        # Stock level recommendations
        if "quantity" not in product_data:
            recommendations.append({
                "priority": "medium",
                "category": "Inventory",
                "fields": ["quantity"],
                "message": "Include stock quantity for real-time inventory visibility",
                "action": "Add quantity field to show available stock"
            })

        # Keywords recommendations
        if "keywords" not in product_data or "tags" not in product_data:
            recommendations.append({
                "priority": "low",
                "category": "SEO Optimization",
                "fields": ["keywords", "tags"],
                "message": "Add keywords and tags for improved searchability",
                "action": "Include relevant keywords and tags for better discovery"
            })

        # Description quality
        if "description" in product_data:
            desc_length = len(str(product_data["description"]))
            if desc_length < 50:
                recommendations.append({
                    "priority": "high",
                    "category": "Content Quality",
                    "fields": ["description"],
                    "message": "Product description is too short",
                    "action": f"Expand description to at least 100 characters (currently {desc_length})"
                })
            elif desc_length > 5000:
                recommendations.append({
                    "priority": "low",
                    "category": "Content Quality",
                    "fields": ["description"],
                    "message": "Product description is very long",
                    "action": "Consider condensing the description while keeping key information"
                })

        self.validation_results["recommendations"] = recommendations

    def _calculate_score(self, product_data: Dict) -> None:
        """
        Calculate product feed completeness score
        
        Score breakdown:
        - Required fields: 60% weight
        - Recommended fields: 30% weight
        - Optional fields: 10% weight
        """
        required = self.schema["required_fields"]
        recommended = self.schema["recommended_fields"]
        optional = self.schema["optional_fields"]

        # Calculate required field score
        required_present = sum(1 for field in required.keys() if field in product_data)
        required_score = (required_present / len(required)) * 60 if required else 0

        # Calculate recommended field score
        recommended_present = sum(1 for field in recommended.keys() if field in product_data)
        recommended_score = (recommended_present / len(recommended)) * 30 if recommended else 0

        # Calculate optional field score
        optional_present = sum(1 for field in optional.keys() if field in product_data)
        optional_score = (optional_present / len(optional)) * 10 if optional else 0

        # Total score
        total_score = min(100, required_score + recommended_score + optional_score)

        self.validation_results["score"] = round(total_score, 2)
        self.validation_results["field_coverage"] = {
            "required": {
                "present": required_present,
                "total": len(required),
                "percentage": round((required_present / len(required) * 100), 2) if required else 0
            },
            "recommended": {
                "present": recommended_present,
                "total": len(recommended),
                "percentage": round((recommended_present / len(recommended) * 100), 2) if recommended else 0
            },
            "optional": {
                "present": optional_present,
                "total": len(optional),
                "percentage": round((optional_present / len(optional) * 100), 2) if optional else 0
            }
        }

    def get_field_details(self, field_name: str) -> Optional[Dict]:
        """Get detailed information about a specific field"""
        for category in ["required_fields", "recommended_fields", "optional_fields"]:
            if field_name in self.schema[category]:
                return {
                    "field": field_name,
                    "category": category.replace("_fields", ""),
                    "specification": self.schema[category][field_name]
                }
        return None


class ProductFeedReviewer:
    """Main application logic for product feed review"""

    def __init__(self):
        self.validator = ChatGPTSchemaValidator()

    def review_product(self, product_data: Dict) -> Dict:
        """Review a single product against ChatGPT specification"""
        return self.validator.validate_product(product_data)

    def review_feed(self, products: List[Dict]) -> Dict:
        """Review complete product feed"""
        results = {
            "total_products": len(products),
            "valid_products": 0,
            "invalid_products": 0,
            "products": [],
            "feed_summary": {
                "avg_score": 0,
                "critical_issues": 0,
                "warnings": 0,
                "common_issues": {}
            }
        }

        all_scores = []
        all_issues = {}

        for idx, product in enumerate(products):
            result = self.review_product(product)
            results["products"].append({
                "index": idx,
                "product_id": product.get("id", f"Unknown-{idx}"),
                "validation": result
            })

            if result["valid"]:
                results["valid_products"] += 1
            else:
                results["invalid_products"] += 1

            all_scores.append(result["score"])

            # Track common issues
            for error in result["errors"]:
                field = error["field"]
                all_issues[field] = all_issues.get(field, 0) + 1

        # Calculate feed-level statistics
        results["feed_summary"]["avg_score"] = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
        results["feed_summary"]["critical_issues"] = results["invalid_products"]
        results["feed_summary"]["warnings"] = sum(
            len(p["validation"]["warnings"]) for p in results["products"]
        )
        results["feed_summary"]["common_issues"] = all_issues

        return results


# Initialize application
reviewer = ProductFeedReviewer()


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/api/validate', methods=['POST'])
def validate_product_api():
    """API endpoint for product validation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Please provide product data in JSON format"
            }), 400

        result = reviewer.review_product(data)
        
        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "error": "Validation failed",
            "message": str(e)
        }), 500


@app.route('/api/validate-feed', methods=['POST'])
def validate_feed_api():
    """API endpoint for batch feed validation"""
    try:
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({
                "error": "Invalid data",
                "message": "Please provide an array of products"
            }), 400

        result = reviewer.review_feed(data)
        
        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        logger.error(f"Feed validation error: {str(e)}")
        return jsonify({
            "error": "Feed validation failed",
            "message": str(e)
        }), 500


@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Get ChatGPT Product Feed Specification schema"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "required_fields": reviewer.validator.schema["required_fields"],
                "recommended_fields": reviewer.validator.schema["recommended_fields"],
                "optional_fields": reviewer.validator.schema["optional_fields"]
            }
        }), 200

    except Exception as e:
        logger.error(f"Schema retrieval error: {str(e)}")
        return jsonify({
            "error": "Schema retrieval failed",
            "message": str(e)
        }), 500


@app.route('/api/field-details/<field_name>', methods=['GET'])
def get_field_details(field_name):
    """Get detailed information about a specific field"""
    try:
        details = reviewer.validator.get_field_details(field_name)
        
        if not details:
            return jsonify({
                "error": "Field not found",
                "message": f"Field '{field_name}' not found in ChatGPT Product Feed Specification"
            }), 404

        return jsonify({
            "success": True,
            "data": details
        }), 200

    except Exception as e:
        logger.error(f"Field details error: {str(e)}")
        return jsonify({
            "error": "Field details retrieval failed",
            "message": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Product Feed Review API"
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
