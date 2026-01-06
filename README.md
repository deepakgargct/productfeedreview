# Product Feed Review

A comprehensive solution for analyzing, validating, and reviewing product feeds with intelligent feedback mechanisms and quality assurance tools.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Functionality
- **Feed Validation**: Comprehensive validation of product feeds against industry standards
- **Quality Analysis**: Automatic detection of data quality issues and inconsistencies
- **Intelligent Feedback**: AI-powered suggestions for feed improvements
- **Multi-Format Support**: Handle CSV, JSON, XML, and custom formats
- **Real-time Processing**: Stream-based processing for large feeds
- **Detailed Reporting**: Generate comprehensive reports with actionable insights

### Advanced Features
- **Schema Validation**: Validate against custom or predefined schemas
- **Duplicate Detection**: Identify and flag duplicate products
- **Price Anomaly Detection**: Detect unusual price fluctuations
- **Image Validation**: Verify image URLs and quality
- **Category Mapping**: Intelligent product category suggestions
- **Competitor Analysis**: Compare feeds with competitor data
- **Historical Tracking**: Monitor feed changes over time
- **Batch Processing**: Handle multiple feeds simultaneously

### Integration Capabilities
- **API-First Design**: RESTful API for easy integration
- **Webhook Support**: Real-time notifications on feed updates
- **Multi-Platform**: Works with e-commerce platforms (Shopify, WooCommerce, Magento)
- **Export Options**: CSV, JSON, PDF, and XML export formats

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip or conda package manager
- 2GB RAM minimum

### Installation (5 minutes)

```bash
# Clone the repository
git clone https://github.com/deepakgargct/productfeedreview.git
cd productfeedreview

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Basic Usage

```python
from productfeedreview import FeedAnalyzer

# Initialize analyzer
analyzer = FeedAnalyzer(config_file='config.yaml')

# Analyze a feed
results = analyzer.analyze('products.csv')

# Get report
report = results.generate_report()
print(report)
```

---

## Installation

### System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.8+ |
| Memory | 2GB minimum |
| Disk Space | 500MB for installation |
| OS | Linux, macOS, Windows |

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/deepakgargct/productfeedreview.git
cd productfeedreview
```

#### 2. Create Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate

# OR using conda
conda create -n productfeedreview python=3.9
conda activate productfeedreview
```

#### 3. Install Dependencies
```bash
# Standard installation
pip install -r requirements.txt

# Development installation
pip install -r requirements-dev.txt

# With optional dependencies
pip install -r requirements.txt[all]
```

#### 4. Configuration
```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env  # or your favorite editor
```

#### 5. Verify Installation
```bash
python -m productfeedreview --version
python -m productfeedreview --help
```

### Docker Installation

```bash
# Build Docker image
docker build -t productfeedreview .

# Run container
docker run -p 8000:8000 productfeedreview

# With volume mount
docker run -p 8000:8000 -v $(pwd)/feeds:/app/feeds productfeedreview
```

---

## Usage

### Command Line Interface

#### Basic Feed Analysis
```bash
# Analyze a single feed
productfeedreview analyze products.csv --format csv

# Analyze with custom schema
productfeedreview analyze products.json --schema custom_schema.json

# Analyze with strict validation
productfeedreview analyze products.xml --strict --report report.html
```

#### Batch Processing
```bash
# Process multiple feeds
productfeedreview batch-process /path/to/feeds --config batch_config.yaml

# Process with parallel execution
productfeedreview batch-process /path/to/feeds --workers 4
```

#### Report Generation
```bash
# Generate HTML report
productfeedreview report --feed products.csv --output report.html

# Generate PDF report
productfeedreview report --feed products.csv --format pdf

# Generate with custom template
productfeedreview report --feed products.csv --template custom.html
```

### Python API

#### Basic Analysis
```python
from productfeedreview import FeedAnalyzer, ValidationSchema

# Initialize analyzer
analyzer = FeedAnalyzer()

# Load and analyze feed
results = analyzer.analyze('products.csv', file_format='csv')

# Access results
print(f"Total products: {results.total_products}")
print(f"Issues found: {results.total_issues}")
print(f"Quality score: {results.quality_score}%")
```

#### Custom Validation
```python
from productfeedreview import ValidationSchema, ValidationRule

# Define custom schema
schema = ValidationSchema(
    name="Custom Product Schema",
    rules=[
        ValidationRule(field='sku', required=True, pattern=r'^[A-Z0-9]{10}$'),
        ValidationRule(field='price', required=True, data_type='float', min_value=0),
        ValidationRule(field='title', required=True, min_length=10, max_length=200),
        ValidationRule(field='url', required=True, validation_type='url'),
    ]
)

# Apply schema
results = analyzer.analyze('products.csv', schema=schema)
```

#### Advanced Processing
```python
from productfeedreview import FeedProcessor, QualityAnalyzer

# Process with custom transformations
processor = FeedProcessor()
processor.add_transformation('normalize_price', {'currency': 'USD'})
processor.add_transformation('standardize_category')
processed_feed = processor.process('products.csv')

# Analyze quality
quality = QualityAnalyzer(processed_feed)
quality_metrics = quality.analyze()

# Generate insights
insights = quality.get_recommendations()
for insight in insights:
    print(f"Issue: {insight.issue}")
    print(f"Severity: {insight.severity}")
    print(f"Recommendation: {insight.recommendation}")
```

#### Working with Results
```python
# Get detailed issues
issues = results.get_issues(severity='critical')

# Filter by category
pricing_issues = results.filter_issues(category='pricing')

# Export results
results.export_csv('analysis_results.csv')
results.export_json('analysis_results.json')
results.export_pdf('analysis_report.pdf')

# Get summary
summary = results.get_summary()
```

---

## API Documentation

### REST API Endpoints

#### Feed Analysis Endpoints

##### POST /api/v1/analyze
Analyze a product feed.

**Request:**
```json
{
  "feed_url": "https://example.com/products.csv",
  "format": "csv",
  "schema_id": "standard_ecommerce",
  "strict_mode": true
}
```

**Response:**
```json
{
  "analysis_id": "ana_123456",
  "status": "completed",
  "total_products": 1500,
  "total_issues": 45,
  "quality_score": 87,
  "issues": [
    {
      "product_id": "SKU-001",
      "field": "price",
      "issue": "Missing price",
      "severity": "critical",
      "suggestion": "Add price for product"
    }
  ],
  "created_at": "2026-01-06T13:13:07Z",
  "processing_time_ms": 2340
}
```

##### GET /api/v1/analysis/{analysis_id}
Retrieve analysis results.

**Response:** Same as above

##### GET /api/v1/analysis/{analysis_id}/report
Download analysis report.

**Query Parameters:**
- `format`: pdf, html, json, csv (default: html)

---

#### Validation Endpoints

##### POST /api/v1/validate
Validate feed against schema.

**Request:**
```json
{
  "feed_data": [...],
  "schema": {
    "fields": [
      {"name": "sku", "required": true, "type": "string"},
      {"name": "price", "required": true, "type": "number"}
    ]
  }
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Some prices are very low"]
}
```

##### GET /api/v1/schemas
List available schemas.

**Response:**
```json
{
  "schemas": [
    {
      "id": "standard_ecommerce",
      "name": "Standard E-commerce",
      "version": "1.0"
    }
  ]
}
```

---

#### Status and Health Endpoints

##### GET /api/v1/health
Check API health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-06T13:13:07Z"
}
```

##### GET /api/v1/status
Get system status.

**Response:**
```json
{
  "status": "operational",
  "active_analyses": 5,
  "queue_length": 2
}
```

---

### Authentication

API requests require authentication via API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.productfeedreview.com/api/v1/analyze
```

Or in Python:
```python
from productfeedreview.client import APIClient

client = APIClient(api_key='your_api_key')
results = client.analyze('products.csv')
```

---

### Error Handling

**Error Response Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Feed validation failed",
    "details": {
      "field": "price",
      "issue": "Invalid price format"
    }
  }
}
```

**Common Error Codes:**
- `VALIDATION_ERROR`: Feed validation failed
- `FILE_NOT_FOUND`: Feed file not found
- `UNSUPPORTED_FORMAT`: Feed format not supported
- `SCHEMA_NOT_FOUND`: Requested schema not found
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Input Layer                             │
│  (CSV, JSON, XML, API, URL, Database, Streaming)           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Parsing & Normalization                    │
│  (Format Detection, Encoding, Data Cleaning)               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               Validation Engine                             │
│  (Schema Validation, Type Checking, Rule Application)      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                Quality Analysis                             │
│  (Completeness, Consistency, Accuracy, Freshness)          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Intelligence & Enrichment                       │
│  (Anomaly Detection, Duplicates, ML Insights)              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Report Generation                          │
│  (Aggregation, Formatting, Export)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Output Layer                             │
│  (JSON, CSV, HTML, PDF, Database, Webhooks)               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Feed Parser
- Handles multiple formats (CSV, JSON, XML, custom)
- Auto-detection of format and encoding
- Streaming support for large files
- Error recovery and partial processing

#### 2. Validation Engine
- Schema-based validation
- Custom rule engine
- Type checking and conversion
- Pattern matching and regex validation

#### 3. Quality Analyzer
- Completeness scoring
- Consistency checking
- Duplicate detection
- Anomaly identification

#### 4. Report Generator
- Structured report creation
- Multiple output formats
- Custom templates
- Aggregated metrics

### Data Flow

1. **Input** → Feed files uploaded/provided
2. **Parse** → Extract and normalize data
3. **Validate** → Check against schema rules
4. **Analyze** → Assess quality and identify issues
5. **Enrich** → Add insights and recommendations
6. **Export** → Generate reports and outputs

### Technology Stack

- **Language**: Python 3.8+
- **Web Framework**: FastAPI / Flask
- **Data Processing**: Pandas, NumPy
- **Validation**: Pydantic, JSONSchema
- **Database**: PostgreSQL / SQLite
- **Cache**: Redis
- **Message Queue**: Celery / RabbitMQ
- **API Documentation**: Swagger/OpenAPI
- **Testing**: Pytest, Coverage
- **Containerization**: Docker, Docker Compose

---

## Examples

### Example 1: Basic CSV Feed Analysis

**Input File (products.csv):**
```csv
sku,title,price,category,url
SKU-001,Widget Pro,$19.99,Electronics,https://example.com/widget-pro
SKU-002,Gadget Plus,,Tools,https://example.com/gadget-plus
SKU-003,Device Max,$-5.00,Electronics,invalid-url
```

**Python Code:**
```python
from productfeedreview import FeedAnalyzer

analyzer = FeedAnalyzer()
results = analyzer.analyze('products.csv', file_format='csv')

print(f"Quality Score: {results.quality_score}%")
print(f"Total Issues: {results.total_issues}")

for issue in results.get_issues(severity='critical'):
    print(f"\nProduct: {issue.product_id}")
    print(f"Issue: {issue.issue}")
    print(f"Suggestion: {issue.suggestion}")
```

**Output:**
```
Quality Score: 73%
Total Issues: 3

Product: SKU-002
Issue: Missing required field 'price'
Suggestion: Add price for product SKU-002

Product: SKU-003
Issue: Invalid price format (negative value)
Suggestion: Correct price to positive value

Product: SKU-003
Issue: Invalid URL format
Suggestion: Provide valid product URL
```

### Example 2: E-commerce Platform Integration

```python
from productfeedreview import FeedAnalyzer, APIClient
from productfeedreview.integrations import ShopifyIntegration

# Initialize Shopify integration
shopify_client = ShopifyIntegration(
    shop_url='myshop.myshopify.com',
    access_token='your_token'
)

# Fetch products from Shopify
products = shopify_client.fetch_products()

# Analyze feed
analyzer = FeedAnalyzer()
results = analyzer.analyze_data(products)

# Generate report
report = results.generate_report()

# Send results back to Shopify via webhook
shopify_client.send_webhook('feed_analysis', report)

print(f"Analysis complete: {results.quality_score}% quality")
```

### Example 3: Batch Processing Multiple Feeds

```python
from productfeedreview import BatchProcessor
from pathlib import Path

# Configure batch processor
config = {
    'workers': 4,
    'timeout': 300,
    'retry_failed': True,
    'generate_reports': True
}

processor = BatchProcessor(config=config)

# Process all feeds in directory
feeds_dir = Path('feeds/')
results = processor.process_directory(feeds_dir)

# Generate summary report
summary = processor.get_summary()
print(f"Processed: {summary['total_feeds']} feeds")
print(f"Avg Quality: {summary['avg_quality_score']}%")
print(f"Total Issues: {summary['total_issues']}")

# Export results
processor.export_results('batch_results.json', format='json')
```

### Example 4: Custom Validation Schema

```python
from productfeedreview import FeedAnalyzer, ValidationSchema, ValidationRule

# Define custom rules
rules = [
    ValidationRule(
        field='sku',
        required=True,
        pattern=r'^[A-Z]{3}-\d{6}$',
        error_message='SKU must match pattern XXX-000000'
    ),
    ValidationRule(
        field='price',
        required=True,
        data_type='float',
        min_value=0.01,
        max_value=10000,
        error_message='Price must be between 0.01 and 10000'
    ),
    ValidationRule(
        field='title',
        required=True,
        min_length=10,
        max_length=200,
        error_message='Title must be 10-200 characters'
    ),
    ValidationRule(
        field='image_url',
        validation_type='url',
        error_message='Invalid image URL'
    ),
]

# Create schema
schema = ValidationSchema(name='Custom E-commerce', rules=rules)

# Analyze with schema
analyzer = FeedAnalyzer()
results = analyzer.analyze('products.json', schema=schema)

# Show validation details
for issue in results.issues:
    print(f"SKU: {issue.product_id}")
    print(f"Field: {issue.field}")
    print(f"Error: {issue.message}")
```

### Example 5: Real-time Feed Monitoring

```python
from productfeedreview import FeedMonitor, AlertManager
import logging

# Setup monitoring
monitor = FeedMonitor(
    feed_url='https://example.com/feed.xml',
    check_interval=3600,  # Check every hour
    quality_threshold=85
)

# Setup alerts
alert_manager = AlertManager()
alert_manager.add_email_alert('admin@example.com')
alert_manager.add_webhook_alert('https://example.com/webhook')

# Start monitoring
monitor.start()

# Listen for issues
@monitor.on_quality_drop
def handle_quality_drop(feed_name, quality_score):
    logging.warning(f"Feed '{feed_name}' quality dropped to {quality_score}%")
    alert_manager.send_alert(
        level='warning',
        message=f"Quality alert for {feed_name}",
        details={'quality_score': quality_score}
    )

@monitor.on_critical_issue
def handle_critical_issue(issue):
    logging.error(f"Critical issue detected: {issue}")
    alert_manager.send_alert(
        level='critical',
        message='Critical issue in feed',
        details=issue
    )

# Keep running
monitor.wait()
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Installation Fails with Dependency Errors

**Error:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Clear pip cache
pip cache purge

# Install with explicit version constraints
pip install -r requirements.txt --no-cache-dir
```

#### Issue 2: Feed Not Being Recognized

**Error:**
```
ERROR: Could not auto-detect feed format
```

**Solution:**
```python
# Explicitly specify format
results = analyzer.analyze('products.txt', file_format='csv', delimiter='\t')

# Or check file encoding
import chardet
with open('products.csv', 'rb') as f:
    encoding = chardet.detect(f.read())['encoding']
print(f"Detected encoding: {encoding}")

# Use correct encoding
results = analyzer.analyze('products.csv', encoding='iso-8859-1')
```

#### Issue 3: Memory Issues with Large Feeds

**Error:**
```
MemoryError: Unable to allocate 2.50 GiB for an array...
```

**Solution:**
```python
# Use streaming mode for large files
analyzer = FeedAnalyzer(streaming=True, chunk_size=5000)
results = analyzer.analyze('large_feed.csv')

# Or process in batches
from productfeedreview import BatchProcessor
processor = BatchProcessor(batch_size=10000)
results = processor.process_large_feed('large_feed.csv')
```

#### Issue 4: API Connection Timeout

**Error:**
```
ConnectionError: Connection timeout after 30s
```

**Solution:**
```python
from productfeedreview.client import APIClient

# Increase timeout
client = APIClient(
    api_key='your_key',
    timeout=120,
    retries=3,
    backoff_factor=0.5
)

# Or for direct feed analysis
results = analyzer.analyze(
    'https://example.com/feed.xml',
    timeout=120,
    verify_ssl=True
)
```

#### Issue 5: Validation Rules Not Applied

**Error:**
```
Validation passed but issues are still present
```

**Solution:**
```python
# Check schema is properly loaded
print(f"Schema: {schema.name}")
print(f"Rules: {schema.rules}")

# Ensure rules are in correct order
schema = ValidationSchema(
    rules=sorted(rules, key=lambda r: r.priority, reverse=True)
)

# Validate schema itself
schema.validate_schema()

# Debug validation
results = analyzer.analyze(
    'products.csv',
    schema=schema,
    debug=True
)
```

#### Issue 6: Docker Container Fails to Start

**Error:**
```
docker: Error response from daemon: driver failed...
```

**Solution:**
```bash
# Check logs
docker logs container_name

# Build with correct base image
docker build --build-arg BASE_IMAGE=python:3.9-slim -t productfeedreview .

# Run with proper resource limits
docker run -m 2g -c 512 productfeedreview

# Check Docker daemon
sudo systemctl restart docker
```

### Performance Optimization

#### For Large Feeds (>100MB):
```python
# Use streaming and parallel processing
analyzer = FeedAnalyzer(
    streaming=True,
    chunk_size=10000,
    workers=4,
    cache_enabled=True
)
```

#### For Batch Operations:
```python
# Configure optimal batch settings
processor = BatchProcessor(
    batch_size=5000,
    workers=8,
    queue_size=100,
    timeout=600
)
```

#### For API Server:
```python
# Use production server with multiple workers
# uvicorn productfeedreview.api:app --workers 4 --loop uvloop
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('productfeedreview')

# Run with verbose output
analyzer = FeedAnalyzer(debug=True, verbose=True)
results = analyzer.analyze('products.csv')
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Commit** your changes (`git commit -am 'Add new feature'`)
4. **Push** to the branch (`git push origin feature/your-feature`)
5. **Submit** a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=productfeedreview

# Run linting
flake8 productfeedreview/
black productfeedreview/

# Build documentation
cd docs && make html
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation**: [https://docs.productfeedreview.com](https://docs.productfeedreview.com)
- **Issues**: [GitHub Issues](https://github.com/deepakgargct/productfeedreview/issues)
- **Email**: support@productfeedreview.com
- **Community**: [Discussions](https://github.com/deepakgargct/productfeedreview/discussions)

---

## Changelog

### Version 1.0.0 (2026-01-06)
- Initial release
- Core feed analysis functionality
- REST API implementation
- Support for CSV, JSON, XML formats
- Quality scoring and issue detection
- Multiple export formats
- Batch processing capabilities

---

**Last Updated**: January 6, 2026  
**Maintained by**: [deepakgargct](https://github.com/deepakgargct)
