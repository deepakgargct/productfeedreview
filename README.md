# Product Feed Review - Custom Schema Tester

A comprehensive tool for validating, analyzing, and testing product feed schemas with support for JSON-LD, custom schemas, and ChatGPT Product Feed specifications.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [File Structure](#file-structure)
- [API Documentation](#api-documentation)
- [JSON-LD Schema Examples](#json-ld-schema-examples)
- [Validation and Error Handling](#validation-and-error-handling)
- [ChatGPT Product Feed Specification](#chatgpt-product-feed-specification)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

Product Feed Review is a powerful validation and testing suite designed to ensure your product feed schemas comply with industry standards and best practices. The tool provides:

- **URL-based schema generation** for quick schema extraction from product feeds
- **Custom Schema Tester** for comprehensive schema validation and analysis
- **Multiple validators** supporting JSON-LD, custom schemas, and ChatGPT specifications
- **Detailed recommendations** for schema improvements and compliance

The application is built with Flask and provides both web interface and API endpoints for easy integration into your workflows.

## ✨ Features

### 1. **URL-Based Schema Generation**
- Automatically extract and parse product feed schemas from URLs
- Support for multiple schema formats and encodings
- Intelligent schema detection and normalization
- Batch processing capabilities

### 2. **Custom Schema Tester**
- Comprehensive validation of custom schema definitions
- Schema completeness analysis
- Field type validation and enforcement
- Recursive schema validation for nested objects
- Performance profiling and optimization suggestions

### 3. **Validators**

#### ChatGPT Schema Validator
- Ensures compliance with ChatGPT Product Feed Specification
- Validates required fields and their formats
- Type checking and format validation
- Product classification support

#### Schema Structure Validator
- Validates against predefined schema specifications
- Type consistency checking
- Required/optional field enforcement
- Format and pattern validation

#### Custom Schema Analyzer
- Deep analysis of custom schema structures
- Missing field detection
- Type inference from sample data
- Recommendations for schema improvements

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Flask 2.0+

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/deepakgargct/productfeedreview.git
cd productfeedreview
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📖 Usage Guide

### Web Interface

1. **Access the application** at `http://localhost:5000`
2. **Enter a product feed URL** in the input field
3. **Select validation options** (ChatGPT compliance, custom schema, etc.)
4. **Click "Analyze"** to run validation
5. **Review results** including errors, warnings, and recommendations

### API Endpoints

#### Validate Schema (POST)
```
POST /api/validate
```

**Request Body:**
```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Wireless Headphones",
    "description": "High-quality wireless headphones",
    "price": "99.99",
    "priceCurrency": "USD",
    "image": "https://example.com/headphones.jpg"
  },
  "validate_chatgpt": true,
  "validate_structure": true
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "recommendations": [
    "Consider adding 'brand' field for better product identification",
    "Add 'availability' field to indicate stock status"
  ],
  "summary": "Schema is valid with minor improvement suggestions"
}
```

#### Extract Schema from URL (POST)
```
POST /api/extract-schema
```

**Request Body:**
```json
{
  "url": "https://example.com/product-feed",
  "validate": true
}
```

**Response:**
```json
{
  "extracted_schemas": [
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Product Name",
      "price": "99.99"
    }
  ],
  "schema_count": 1,
  "validation_results": {}
}
```

#### Analyze Custom Schema (POST)
```
POST /api/analyze-custom-schema
```

**Request Body:**
```json
{
  "schema_definition": {
    "type": "object",
    "properties": {
      "product_id": {"type": "string"},
      "product_name": {"type": "string"},
      "pricing": {
        "type": "object",
        "properties": {
          "amount": {"type": "number"},
          "currency": {"type": "string"}
        }
      }
    },
    "required": ["product_id", "product_name"]
  },
  "sample_data": {
    "product_id": "SKU123",
    "product_name": "Headphones"
  }
}
```

**Response:**
```json
{
  "completeness": 85,
  "missing_fields": ["description", "image_url"],
  "type_consistency": true,
  "recommendations": [
    "Add 'description' field for better product context",
    "Include 'image_url' for product visualization"
  ],
  "analysis": {
    "total_fields": 3,
    "required_fields": 2,
    "optional_fields": 1
  }
}
```

### Command Line Usage

#### Validate a JSON-LD Schema
```bash
python custom_schema_tester.py --validate --file schema.json
```

#### Analyze Custom Schema
```bash
python custom_schema_tester.py --analyze --file custom_schema.json --sample-data sample.json
```

#### Extract Schema from URL
```bash
python custom_schema_tester.py --extract --url https://example.com/product
```

## 📁 File Structure

```
productfeedreview/
├── app.py                           # Main Flask application
├── custom_schema_tester.py          # Custom schema testing utility
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── validators/
│   ├── __init__.py
│   ├── chatgpt_schema_spec.py      # ChatGPT Product Feed Specification
│   ├── schema_validator.py         # Schema validation logic
│   └── custom_schema_analyzer.py   # Custom schema analysis
│
├── templates/
│   ├── base.html                   # Base template
│   ├── index.html                  # Home page
│   └── results.html                # Results display page
│
├── static/
│   ├── css/
│   │   └── style.css               # Application styling
│   └── js/
│       └── main.js                 # Frontend JavaScript
│
└── tests/
    ├── test_validators.py          # Validator unit tests
    ├── test_schema_tester.py       # Schema tester tests
    └── test_api.py                 # API endpoint tests
```

### Key Components

#### **app.py** - Flask Application
Main application file containing:
- Route handlers for web interface
- REST API endpoints
- Request/response handling
- Error management

#### **custom_schema_tester.py** - Schema Testing Utility
Core testing logic:
- Schema extraction and parsing
- Validation orchestration
- Results aggregation
- CLI interface

#### **validators/chatgpt_schema_spec.py** - ChatGPT Specification
ChatGPT Product Feed requirements:
```python
CHATGPT_REQUIRED_FIELDS = {
    'name': {'type': 'string'},
    'price': {'type': 'number'},
    'priceCurrency': {'type': 'string'},
    'description': {'type': 'string'},
    'image': {'type': 'string' or 'array'}
}

CHATGPT_OPTIONAL_FIELDS = {
    'brand': {'type': 'string'},
    'availability': {'type': 'string'},
    'review': {'type': 'object'},
    'ratingValue': {'type': 'number'}
}
```

#### **validators/schema_validator.py** - Validation Engine
Core validation functionality:
- Schema structure validation
- Type checking
- Required field enforcement
- Format validation
- Error reporting

#### **validators/custom_schema_analyzer.py** - Analysis Tool
Schema analysis features:
- Completeness scoring
- Missing field detection
- Type consistency checking
- Recommendation generation

## 🔗 API Documentation

### Authentication

Currently, the API is open. For production deployments, implement API key authentication:

```python
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or not validate_api_key(api_key):
        return {'error': 'Invalid API key'}, 401
```

### Error Responses

All API endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "status": 400,
  "details": {
    "field": "Additional error details"
  }
}
```

### Rate Limiting

Recommended rate limiting configuration:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users
- Burst limit: 20 requests

### Response Codes

- **200**: Successful request
- **400**: Bad request (invalid input)
- **401**: Unauthorized (missing/invalid API key)
- **422**: Unprocessable entity (validation failed)
- **500**: Internal server error

## 📊 JSON-LD Schema Examples

### Basic Product Schema

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Wireless Bluetooth Headphones",
  "description": "Premium wireless headphones with active noise cancellation",
  "image": "https://example.com/images/headphones.jpg",
  "brand": {
    "@type": "Brand",
    "name": "AudioTech"
  },
  "price": "149.99",
  "priceCurrency": "USD",
  "availability": "https://schema.org/InStock",
  "review": {
    "@type": "Review",
    "ratingValue": "4.5",
    "reviewRating": {
      "@type": "Rating",
      "ratingValue": "4.5",
      "bestRating": "5",
      "worstRating": "1"
    },
    "reviewCount": "328"
  }
}
```

### Product with Aggregate Rating

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Smart Watch Pro",
  "image": "https://example.com/smartwatch.jpg",
  "description": "Advanced fitness tracking smartwatch",
  "brand": {
    "@type": "Brand",
    "name": "TechBrand"
  },
  "price": "299.99",
  "priceCurrency": "USD",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.6",
    "ratingCount": "1250",
    "bestRating": "5",
    "worstRating": "1"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/buy/smartwatch",
    "priceCurrency": "USD",
    "price": "299.99",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Example Store"
    }
  }
}
```

### Product with Multiple Offers

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Laptop Computer",
  "brand": {
    "@type": "Brand",
    "name": "CompanyName"
  },
  "image": "https://example.com/laptop.jpg",
  "description": "High-performance laptop for professionals",
  "offers": [
    {
      "@type": "Offer",
      "url": "https://retailer1.com/laptop",
      "priceCurrency": "USD",
      "price": "999.99",
      "availability": "https://schema.org/InStock",
      "seller": {
        "@type": "Organization",
        "name": "Retailer One"
      }
    },
    {
      "@type": "Offer",
      "url": "https://retailer2.com/laptop",
      "priceCurrency": "USD",
      "price": "1049.99",
      "availability": "https://schema.org/InStock",
      "seller": {
        "@type": "Organization",
        "name": "Retailer Two"
      }
    }
  ]
}
```

## ✅ Validation and Error Handling

### Common Validation Errors

#### Missing Required Fields

**Error Message:**
```
MISSING_REQUIRED_FIELD: Field 'name' is required but not provided
Severity: ERROR
Fix: Add 'name' field to your schema
```

**Example Fix:**
```json
{
  "@type": "Product",
  "name": "Product Name",  // ADDED
  "price": "99.99"
}
```

#### Invalid Type

**Error Message:**
```
INVALID_TYPE: Field 'price' should be 'number' but got 'string'
Severity: ERROR
Current Value: "99.99"
Expected Type: number
```

**Example Fix:**
```json
{
  "price": 99.99  // Changed from string to number
}
```

#### Malformed URL

**Error Message:**
```
INVALID_URL: Field 'image' contains invalid URL format
Severity: WARNING
Current Value: "not-a-url"
Suggested Format: "https://example.com/image.jpg"
```

**Example Fix:**
```json
{
  "image": "https://example.com/product-image.jpg"
}
```

### Validation Examples

#### Successful Validation

```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Wireless Headphones",
      "price": 99.99,
      "priceCurrency": "USD",
      "image": "https://example.com/headphones.jpg"
    },
    "validate_chatgpt": true
  }'
```

**Response:**
```json
{
  "valid": true,
  "validation_type": "COMPREHENSIVE",
  "errors": [],
  "warnings": [],
  "recommendations": [
    "Consider adding 'brand' field for better product identification",
    "Add 'availability' field to indicate stock status",
    "Include 'description' for better product context"
  ],
  "summary": "Schema is valid according to ChatGPT Product Feed Specification"
}
```

#### Failed Validation

```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "@context": "https://schema.org",
      "@type": "Product",
      "price": "not_a_number"
    },
    "validate_chatgpt": true
  }'
```

**Response:**
```json
{
  "valid": false,
  "validation_type": "COMPREHENSIVE",
  "errors": [
    {
      "field": "name",
      "message": "MISSING_REQUIRED_FIELD: 'name' is required",
      "severity": "ERROR",
      "fix": "Add 'name' field to your schema"
    },
    {
      "field": "price",
      "message": "INVALID_TYPE: 'price' should be number but got string",
      "severity": "ERROR",
      "fix": "Change price value to a number without quotes"
    },
    {
      "field": "priceCurrency",
      "message": "MISSING_REQUIRED_FIELD: 'priceCurrency' is required",
      "severity": "ERROR",
      "fix": "Add 'priceCurrency' field (e.g., 'USD', 'EUR')"
    },
    {
      "field": "image",
      "message": "MISSING_REQUIRED_FIELD: 'image' is required",
      "severity": "ERROR",
      "fix": "Add valid product image URL"
    }
  ],
  "warnings": [],
  "recommendations": [
    "Complete all required fields before proceeding",
    "Validate data types match the specification"
  ],
  "summary": "Schema has 4 critical errors that must be fixed"
}
```

### Recommendations Engine

The validator provides intelligent recommendations:

```json
{
  "recommendations": [
    {
      "field": "brand",
      "type": "ENHANCEMENT",
      "priority": "HIGH",
      "message": "Adding 'brand' field helps with product differentiation",
      "example": {
        "@type": "Brand",
        "name": "Your Brand Name"
      }
    },
    {
      "field": "aggregateRating",
      "type": "SEO_IMPROVEMENT",
      "priority": "MEDIUM",
      "message": "Aggregate ratings improve search visibility",
      "example": {
        "@type": "AggregateRating",
        "ratingValue": "4.5",
        "ratingCount": "123"
      }
    },
    {
      "field": "availability",
      "type": "BEST_PRACTICE",
      "priority": "HIGH",
      "message": "Availability status helps users understand product stock",
      "example": "https://schema.org/InStock"
    }
  ]
}
```

## 🎓 ChatGPT Product Feed Specification

### Compliance Requirements

Product Feed Review validates against the ChatGPT Product Feed Specification, which includes:

#### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `@context` | URL | Schema.org context | "https://schema.org" |
| `@type` | String | Must be "Product" | "Product" |
| `name` | String | Product name | "Wireless Headphones" |
| `description` | String | Product description | "High-quality audio" |
| `price` | Number | Product price | 99.99 |
| `priceCurrency` | String | ISO 4217 currency code | "USD" |
| `image` | String/Array | Product image URL(s) | "https://example.com/image.jpg" |

#### Recommended Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `brand` | Object/String | Product brand | { "@type": "Brand", "name": "BrandName" } |
| `availability` | URL | Stock availability | "https://schema.org/InStock" |
| `aggregateRating` | Object | Aggregate ratings | { "@type": "AggregateRating", "ratingValue": 4.5 } |
| `review` | Array | Product reviews | [{ "@type": "Review", "ratingValue": "5" }] |
| `url` | URL | Product URL | "https://example.com/product" |
| `offers` | Object/Array | Purchase options | [{ "@type": "Offer", "price": "99.99" }] |

#### Best Practices for ChatGPT Compatibility

1. **Always include product images** - Multiple images for better representation
2. **Use structured pricing** - Always separate price and currency
3. **Add ratings and reviews** - Improves product credibility
4. **Include brand information** - Helps product identification
5. **Specify availability** - Indicates stock status to users
6. **Use valid URLs** - All URLs must be properly formatted and accessible

### Validation Checklist

- [ ] Schema includes `@context: "https://schema.org"`
- [ ] `@type` is set to "Product"
- [ ] All required fields are present and non-empty
- [ ] Field values match their expected types
- [ ] URLs are valid and properly formatted
- [ ] Currency codes follow ISO 4217 standard
- [ ] Price is a valid number
- [ ] Image URLs are accessible and return valid images
- [ ] Rating values are between 0 and 5
- [ ] Review count is a positive integer

## 🏆 Best Practices

### 1. Schema Organization

**Good Practice:**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Clear Product Name",
  "description": "Detailed product description...",
  "image": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
  "brand": {
    "@type": "Brand",
    "name": "Brand Name"
  },
  "price": 99.99,
  "priceCurrency": "USD",
  "availability": "https://schema.org/InStock"
}
```

**Avoid:**
```json
{
  "@type": "Product",
  "name": "Product",
  "price": "99.99",  // Should be number, not string
  "image": "url1, url2"  // Should be array, not comma-separated string
}
```

### 2. Image Best Practices

- **Size**: Provide multiple image sizes (thumbnail, medium, large)
- **Format**: Use web-friendly formats (JPEG, PNG, WebP)
- **Quantity**: Include at least 3 high-quality images
- **Accessibility**: Add alt text descriptions
- **Hosting**: Use reliable, fast-loading image servers

**Example:**
```json
{
  "image": [
    "https://example.com/images/product-main.jpg",
    "https://example.com/images/product-side1.jpg",
    "https://example.com/images/product-side2.jpg",
    "https://example.com/images/product-detail.jpg"
  ]
}
```

### 3. Pricing Best Practices

- **Always separate price and currency** - Never combine in one field
- **Use numeric values** - No currency symbols in price field
- **Update regularly** - Keep prices current and accurate
- **Show all fees** - Include shipping, taxes when applicable
- **Compare with competitors** - Ensure competitive pricing

**Example:**
```json
{
  "price": 99.99,
  "priceCurrency": "USD",
  "offers": {
    "@type": "Offer",
    "price": "99.99",
    "priceCurrency": "USD",
    "shippingPrice": {
      "price": "10.00",
      "priceCurrency": "USD"
    }
  }
}
```

### 4. Description Best Practices

- **Be specific and detailed** - Minimum 100 characters
- **Highlight key features** - What makes it unique
- **Use clear language** - Avoid jargon
- **Include specifications** - Size, material, color, etc.
- **Add benefits** - Why customers should buy

**Example:**
```json
{
  "description": "Premium wireless headphones featuring active noise cancellation, 30-hour battery life, premium sound quality with 40mm drivers, Bluetooth 5.0 connectivity, built-in microphone for calls, and comfortable over-ear design. Perfect for music enthusiasts and professionals."
}
```

### 5. Ratings and Reviews

- **Include aggregate ratings** - Overall product rating
- **Show review count** - Number of reviews backing the rating
- **Add individual reviews** - Real customer feedback
- **Update regularly** - Keep ratings current
- **Encourage reviews** - More reviews = higher trust

**Example:**
```json
{
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "ratingCount": "542",
    "bestRating": "5",
    "worstRating": "1"
  },
  "review": [
    {
      "@type": "Review",
      "author": "John Doe",
      "datePublished": "2025-12-20",
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5",
        "bestRating": "5",
        "worstRating": "1"
      },
      "reviewBody": "Excellent product! Exceeded my expectations."
    }
  ]
}
```

### 6. Availability Management

- **Use standard schema.org values**:
  - `https://schema.org/InStock` - Item is available
  - `https://schema.org/OutOfStock` - Item is unavailable
  - `https://schema.org/PreOrder` - Item available for pre-order
  - `https://schema.org/BackOrder` - Item can be back-ordered

- **Include stock quantity** - Helps with inventory management
- **Add delivery information** - Expected delivery date/timeframe

**Example:**
```json
{
  "availability": "https://schema.org/InStock",
  "inventoryLevel": {
    "@type": "QuantitativeValue",
    "value": 145
  },
  "shippingDetails": {
    "@type": "ShippingDeliveryTime",
    "handlingTime": {
      "@type": "QuantitativeValue",
      "unitCode": "DAY",
      "value": "1"
    },
    "transitTime": {
      "@type": "QuantitativeValue",
      "unitCode": "DAY",
      "value": "2"
    }
  }
}
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Invalid JSON Syntax"

**Symptoms:** Validation fails immediately with parsing error

**Causes:**
- Trailing commas in JSON
- Missing quotes around strings
- Invalid escape sequences
- Unmatched braces or brackets

**Solution:**
```bash
# Validate JSON syntax using Python
python -m json.tool your_schema.json

# Or use online validators
# https://jsonlint.com/
# https://www.jsonschemavalidator.com/
```

**Example Fix:**
```json
// WRONG - Trailing comma
{
  "name": "Product",
  "price": 99.99,  // ← Trailing comma
}

// CORRECT
{
  "name": "Product",
  "price": 99.99
}
```

#### Issue 2: "Missing Required Field: name"

**Symptoms:** Validation fails with missing field error

**Causes:**
- Field name is missing entirely
- Field is empty string or null
- Field name has typo (case-sensitive)

**Solution:**
```json
// Check field names are exact (case-sensitive)
// ChatGPT spec expects lowercase camelCase

{
  "Name": "Product"  // ❌ WRONG - capital N
}

{
  "name": "Product"  // ✅ CORRECT
}
```

#### Issue 3: "Invalid Price Format"

**Symptoms:** Price validation fails

**Causes:**
- Price is a string instead of number
- Price contains currency symbols
- Price has incorrect decimal places
- Price is negative

**Solution:**
```json
// WRONG - Multiple issues
{
  "price": "$99.99",     // String with symbol
  "price": "99,99"       // Wrong decimal separator
  "price": "-50.00"      // Negative price
}

// CORRECT
{
  "price": 99.99         // Number, no symbol
}
```

#### Issue 4: "Invalid Image URL"

**Symptoms:** Image validation fails or images don't load

**Causes:**
- URL is malformed
- URL is not accessible
- URL uses incorrect protocol (http vs https)
- Image file format not supported

**Solution:**
```bash
# Test URL accessibility
curl -I https://example.com/image.jpg

# Check for proper HTTPS
# Ensure .jpg, .png, .webp extensions
# Verify file exists and is not a redirect
```

**Example Fix:**
```json
// WRONG
{
  "image": "example.com/image.jpg"        // Missing protocol
}

// CORRECT
{
  "image": "https://example.com/image.jpg"  // Valid HTTPS URL
}
```

#### Issue 5: "Invalid Currency Code"

**Symptoms:** Currency validation fails

**Causes:**
- Currency code is not ISO 4217 compliant
- Lowercase or mixed case currency codes
- Typos in currency abbreviation

**Solution:**
```json
// WRONG
{
  "priceCurrency": "usd"      // Lowercase
  "priceCurrency": "DOLLARS"  // Not ISO 4217
}

// CORRECT
{
  "priceCurrency": "USD"      // ISO 4217 uppercase
}
```

**Common ISO 4217 Codes:**
- USD - US Dollar
- EUR - Euro
- GBP - British Pound
- JPY - Japanese Yen
- CAD - Canadian Dollar
- AUD - Australian Dollar
- CHF - Swiss Franc
- CNY - Chinese Yuan

#### Issue 6: "Invalid Rating Value"

**Symptoms:** Rating validation fails

**Causes:**
- Rating is outside 0-5 range
- Rating is string instead of number
- Rating count is negative or zero

**Solution:**
```json
// WRONG
{
  "aggregateRating": {
    "ratingValue": "8.5",     // Out of range (0-5)
    "ratingCount": "-10"      // Negative count
  }
}

// CORRECT
{
  "aggregateRating": {
    "ratingValue": 4.5,       // Number between 0-5
    "ratingCount": 542        // Positive integer
  }
}
```

#### Issue 7: "URL Not Accessible"

**Symptoms:** Schema extraction from URL fails

**Causes:**
- URL is incorrect or has typos
- Server is down or not responding
- Request is blocked by CORS or firewall
- URL requires authentication

**Solution:**
```bash
# Test URL from command line
curl -v https://example.com/product-feed

# Check for CORS issues
# Add proper user-agent if required
# Check network connectivity
```

**Workaround:**
```bash
# Extract schema manually and use direct upload instead
python custom_schema_tester.py --validate --file schema.json
```

#### Issue 8: "Connection Timeout"

**Symptoms:** API requests timeout

**Causes:**
- Server is slow or overloaded
- Network connectivity issues
- Request payload too large
- Server configuration limits

**Solution:**
```python
# Increase timeout in requests
import requests

response = requests.post(
    'http://localhost:5000/api/validate',
    json=payload,
    timeout=30  # 30 seconds
)
```

**Prevention:**
- Keep request payload under 1MB
- Optimize server performance
- Implement caching for repeated requests
- Use connection pooling

### Debug Mode

Enable debug mode for detailed error messages:

```bash
# Set environment variable
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run application
python app.py
```

### Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Validation started for schema")
```

### Performance Optimization

For large schemas or batch processing:

```bash
# Use threading for parallel validation
python custom_schema_tester.py --batch --file schemas.jsonl --workers 4

# Monitor resource usage
top -p $(pgrep -f "python app.py")

# Profile code
python -m cProfile app.py
```

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📧 Support

For support, questions, or bug reports:
- Open an issue on GitHub
- Contact: [your-email@example.com]
- Documentation: Check the [Wiki](https://github.com/deepakgargct/productfeedreview/wiki)

## 🔄 Version History

### v1.0.0 (2026-01-06)
- Initial release
- ChatGPT schema validation
- Custom schema testing
- URL-based schema extraction
- REST API endpoints
- Web interface

---

**Last Updated:** 2026-01-06 12:33:12 UTC
**Maintained by:** deepakgargct