# Enhanced Product Feed Review System - User Guide

## Overview

The Enhanced Product Feed Review System provides comprehensive validation of product feeds against ChatGPT Product Feed Specifications with advanced compliance scoring, critical issue detection, and actionable recommendations.

## Key Features

### ✅ Compliance Scoring
- **0-100% Compliance Score**: Each product receives a compliance score based on ChatGPT specifications
- **Color-coded Results**: Excellent (90%+), Good (70-89%), Fair (50-69%), Poor (<50%)
- **Prominent Display**: Large, visually appealing compliance metric

### 🔴 Critical Issue Detection
- **Red Highlighting**: Critical issues are prominently displayed in red
- **Severity Classification**: CRITICAL, WARNING, INFO levels
- **Detailed Messages**: Clear explanations of what's wrong

### 💡 Actionable Recommendations
- **Specific Actions**: Each recommendation includes what to do
- **Field-specific**: Targeted suggestions for each field
- **Best Practices**: Aligned with ChatGPT product specifications

### 📦 Batch Processing
- **CSV Upload**: Validate entire CSV product feeds
- **JSON Upload**: Validate JSON arrays or files
- **Batch Summary**: Overall compliance metrics
- **Per-product Details**: Detailed results for each product

### 📊 Export Capabilities
- **JSON Reports**: Complete validation results
- **CSV Summaries**: Tabular format for easy analysis
- **Downloadable**: Export results for documentation

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### 1. Start the API Server

```bash
python api_server.py
```

The API server will start on `http://localhost:5000`

### 2. Start the Streamlit UI

```bash
streamlit run streamlit_enhanced_validator.py
```

The UI will open in your browser at `http://localhost:8501`

## Usage

### Single Product Validation

#### Method 1: Manual Entry
1. Select "Single Product Validation" from the sidebar
2. Choose "Manual Entry"
3. Fill in the product details:
   - **Required**: Product ID, Title, Description, Price, Currency, Category, Availability
   - **Optional**: Brand, Image URL, Product URL, Rating
4. Click "✅ Validate Product"
5. Review compliance score and issues

#### Method 2: JSON Paste
1. Select "JSON Paste" as input method
2. Paste your product JSON
3. Click "✅ Validate JSON"

Example:
```json
{
    "product_id": "PROD001",
    "title": "Premium Wireless Headphones",
    "description": "High-quality wireless headphones with active noise cancellation",
    "price": 149.99,
    "currency": "USD",
    "category": "electronics",
    "availability": "in_stock"
}
```

#### Method 3: Sample Product
1. Select "Sample Product"
2. Click "📦 Load Sample & Validate"
3. See example validation results

### Batch Feed Validation

1. Select "Batch Feed Validation" from the sidebar
2. Upload a CSV or JSON file
3. Preview the file contents
4. Click "✅ Validate Feed"
5. Review batch summary and individual product results

#### CSV Format Example
```csv
product_id,title,description,price,currency,category,availability
PROD001,Wireless Headphones,High-quality audio device,149.99,USD,electronics,in_stock
PROD002,USB Cable,Fast charging cable,15.99,USD,electronics,in_stock
```

#### JSON Format Example
```json
[
    {
        "product_id": "PROD001",
        "title": "Wireless Headphones",
        "description": "High-quality audio device",
        "price": 149.99,
        "currency": "USD",
        "category": "electronics",
        "availability": "in_stock"
    }
]
```

## API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
    "status": "healthy",
    "service": "Product Feed Review API",
    "version": "2.0",
    "timestamp": "2026-01-06 13:00:00"
}
```

### POST /api/validate
Validate a single product

**Request:**
```json
{
    "product_id": "PROD001",
    "title": "Product Name",
    "description": "Product description",
    "price": 99.99,
    "currency": "USD",
    "category": "electronics",
    "availability": "in_stock"
}
```

**Response:**
```json
{
    "product_id": "PROD001",
    "valid": true,
    "compliance_score": 86.0,
    "compliance_percentage": "86.0%",
    "is_compliant": true,
    "critical_issues": [],
    "warnings": [],
    "recommendations": [],
    "summary": {
        "total_critical": 0,
        "total_warnings": 0,
        "total_recommendations": 0
    },
    "timestamp": "2026-01-06 13:00:00"
}
```

### POST /api/validate-feed
Validate batch products (JSON array or file upload)

**Request (JSON):**
```json
[
    {
        "product_id": "PROD001",
        "title": "Product 1",
        ...
    },
    {
        "product_id": "PROD002",
        "title": "Product 2",
        ...
    }
]
```

**Request (File Upload):**
```bash
curl -X POST http://localhost:5000/api/validate-feed \
  -F "file=@products.csv"
```

**Response:**
```json
{
    "batch_summary": {
        "total_products": 2,
        "compliant_products": 1,
        "non_compliant_products": 1,
        "compliance_rate": "50.0%",
        "average_compliance_score": 65.0,
        "total_critical_issues": 3,
        "total_warnings": 2,
        "total_recommendations": 1
    },
    "products": [
        {
            "product_id": "PROD001",
            "valid": true,
            "compliance_score": 86.0,
            ...
        },
        {
            "product_id": "PROD002",
            "valid": false,
            "compliance_score": 44.0,
            ...
        }
    ],
    "timestamp": "2026-01-06 13:00:00"
}
```

### GET /api/info
Get API information

**Response:**
```json
{
    "service": "Product Feed Review API",
    "version": "2.0.0",
    "endpoints": {
        "GET /health": "Health check endpoint",
        "GET /api/info": "API information",
        "POST /api/validate": "Validate a single product",
        "POST /api/validate-feed": "Batch validate products"
    },
    "features": [
        "ChatGPT Product Specification compliance",
        "Compliance score (0-100%)",
        "Critical issue identification",
        "Actionable recommendations",
        "CSV and JSON batch processing"
    ]
}
```

## ChatGPT Product Specification Requirements

### Required Fields
- **product_id**: Unique product identifier
- **title**: Product title (10-150 characters)
- **description**: Product description (20-5000 characters)
- **price**: Product price (> 0.01)
- **currency**: ISO 4217 currency code (USD, EUR, GBP, etc.)
- **category**: Product category
- **availability**: Stock status (in_stock, out_of_stock, preorder)

### Recommended Fields
- **image_url**: Product image URL (HTTPS)
- **product_url**: Product landing page URL (HTTPS)
- **rating**: Product rating (0-5)
- **review_count**: Number of reviews
- **manufacturer**: Product brand/manufacturer
- **sku**: Stock keeping unit
- **stock_quantity**: Available inventory

### Validation Rules

1. **Title**: 10-150 characters, no excessive keywords
2. **Description**: 20-5000 characters, quality content
3. **Price**: Positive number, reasonable range
4. **Currency**: Valid ISO 4217 code (uppercase)
5. **Category**: Standard categories (electronics, clothing, etc.)
6. **Availability**: Standard values (in_stock, out_of_stock, preorder)
7. **URLs**: Valid HTTPS URLs
8. **Rating**: 0-5 range

## Compliance Score Calculation

The compliance score is calculated based on:

1. **Required Fields** (60 points max):
   - Each missing required field: -10 points
   - Each invalid required field: -10 points

2. **Field Quality** (30 points max):
   - Poor description quality: -3 points
   - Invalid URL formats: -3 points each
   - Out-of-range values: -3 points

3. **Recommended Fields** (10 points max):
   - Missing image_url: -2 points
   - Missing product_url: -2 points
   - Missing rating: -1 point
   - Missing other recommended fields: -1 point each

**Final Score**: 100 - total deductions (minimum 0)

## Examples

### Valid Product Example
```json
{
    "product_id": "HEADPHONE001",
    "title": "Premium Wireless Bluetooth Headphones",
    "description": "High-quality wireless headphones with active noise cancellation, 30-hour battery life, and premium sound quality. Perfect for music lovers.",
    "price": 149.99,
    "currency": "USD",
    "category": "electronics",
    "availability": "in_stock",
    "image_url": "https://example.com/headphones.jpg",
    "product_url": "https://example.com/products/headphones",
    "manufacturer": "AudioPro",
    "rating": 4.5,
    "review_count": 1250
}
```

**Compliance Score**: 96%
- All required fields present
- Quality description
- Valid URLs
- All recommended fields included

### Invalid Product Example
```json
{
    "product_id": "BAD001",
    "title": "Short",
    "description": "Bad",
    "price": -10,
    "currency": "INVALID",
    "category": "unknown",
    "availability": "maybe"
}
```

**Compliance Score**: 44%

**Critical Issues**:
- Title too short (< 10 characters)
- Description too short (< 20 characters)
- Price is negative

**Warnings**:
- Invalid currency code
- Non-standard category
- Non-standard availability status

## Troubleshooting

### API Server Won't Start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process
kill <PID>

# Restart server
python api_server.py
```

### Streamlit UI Won't Connect to API
1. Verify API server is running: `curl http://localhost:5000/health`
2. Check firewall settings
3. Ensure both services are on the same network

### File Upload Fails
1. Check file size (max 16MB)
2. Verify file format (CSV or JSON)
3. Ensure proper CSV headers or JSON structure

### Low Compliance Scores
1. Review critical issues first (red highlighting)
2. Address warnings (yellow highlighting)
3. Add recommended fields
4. Follow ChatGPT product specification requirements

## Best Practices

1. **Always Fix Critical Issues**: These prevent products from being valid
2. **Address Warnings**: Improve overall quality
3. **Add Recommended Fields**: Boost compliance score
4. **Use Quality Descriptions**: Detailed, informative content
5. **Validate URLs**: Ensure all URLs are accessible
6. **Regular Updates**: Keep product data current
7. **Batch Processing**: Validate entire feeds regularly

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Examine sample files
4. Check validation logs

## Version History

### Version 2.0 (2026-01-06)
- ✅ Added compliance scoring (0-100%)
- 🔴 Implemented critical issue detection
- 💡 Added actionable recommendations
- 📦 Added CSV/JSON batch processing
- 📊 Enhanced UI with prominent metrics
- 🎨 Color-coded issue highlighting
- 📥 Export capabilities

### Version 1.0
- Basic validation
- Single product support
- Simple error reporting
