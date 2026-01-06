# Product Feed Validator - Comprehensive Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Feed Format Specifications](#feed-format-specifications)
8. [Validation Rules](#validation-rules)
9. [Error Handling](#error-handling)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting](#troubleshooting)
12. [Contributing](#contributing)
13. [FAQ](#faq)

---

## Project Overview

The **Product Feed Validator** is a robust tool designed to validate and review product feed data from various e-commerce platforms and data sources. This project ensures that product feeds meet specified quality standards and conform to required format specifications.

### Purpose
- Validate product feed formats and structure
- Ensure data integrity and completeness
- Detect and report feed anomalies
- Support multiple feed formats (CSV, XML, JSON)
- Enable data quality assurance for e-commerce operations

### Target Users
- E-commerce platform operators
- Data analysts
- Quality assurance teams
- Integration specialists
- Product data managers

---

## Features

### Core Features
- ✅ **Multi-Format Support**: Validate CSV, XML, and JSON feed formats
- ✅ **Comprehensive Validation**: Check for required fields, data types, and value ranges
- ✅ **Duplicate Detection**: Identify duplicate product entries
- ✅ **Data Integrity Checks**: Validate relationships between fields
- ✅ **Custom Rules Engine**: Define and apply custom validation rules
- ✅ **Detailed Reporting**: Generate comprehensive validation reports
- ✅ **Error Categorization**: Classify errors by severity (Critical, Warning, Info)
- ✅ **Batch Processing**: Handle large feed files efficiently
- ✅ **Schema Validation**: Support for custom schema definitions

### Advanced Features
- 📊 **Statistical Analysis**: Feed statistics and trends
- 🔍 **Pattern Detection**: Identify common issues and patterns
- 📈 **Performance Metrics**: Track validation performance
- 🔗 **Integration APIs**: RESTful API for programmatic access
- 📝 **Custom Validation Rules**: Define business-specific rules
- 💾 **Results Caching**: Cache validation results for improved performance

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/deepakgargct/productfeedreview.git
   cd productfeedreview
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python -m pytest tests/
   ```

### Docker Setup

```bash
docker build -t product-feed-validator .
docker run -v /path/to/feeds:/data product-feed-validator
```

---

## Configuration

### Configuration File Structure

Create a `config.yml` file in the project root:

```yaml
validation:
  strict_mode: true
  max_file_size: 500  # MB
  timeout: 300  # seconds
  
feeds:
  required_fields:
    - product_id
    - product_name
    - price
    - availability
  
  optional_fields:
    - description
    - image_url
    - category

quality_thresholds:
  min_valid_percentage: 95
  max_duplicate_percentage: 5
  max_null_percentage: 10

reporting:
  output_format: json  # json, csv, html
  include_samples: true
  detailed_errors: true
```

### Environment Variables

```bash
FEED_VALIDATOR_MODE=production  # development, production
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
MAX_WORKERS=4
```

---

## Usage Guide

### Command Line Interface

#### Basic Validation
```bash
python -m feedvalidator validate --file products.csv
```

#### Validate with Custom Rules
```bash
python -m feedvalidator validate --file products.json --rules custom_rules.json
```

#### Generate Report
```bash
python -m feedvalidator validate --file products.xml --report results.html
```

#### Batch Processing
```bash
python -m feedvalidator batch --directory /path/to/feeds --pattern "*.csv"
```

### Python API

#### Simple Validation
```python
from feedvalidator import ProductFeedValidator

validator = ProductFeedValidator()
results = validator.validate_file('products.csv')

print(f"Valid records: {results.valid_count}")
print(f"Errors: {results.error_count}")
print(f"Validation score: {results.score}%")
```

#### Advanced Validation with Custom Rules
```python
from feedvalidator import ProductFeedValidator, CustomRules

# Define custom validation rules
rules = CustomRules()
rules.add_rule('price_positive', lambda x: x['price'] > 0)
rules.add_rule('valid_sku', lambda x: len(x['sku']) >= 5)

validator = ProductFeedValidator(custom_rules=rules)
results = validator.validate_file('products.json', format='json')

# Access detailed results
for error in results.errors:
    print(f"Row {error['row_number']}: {error['message']}")
```

#### Processing Large Files
```python
from feedvalidator import FeedProcessor

processor = FeedProcessor(
    chunk_size=10000,
    max_workers=4
)

for batch_results in processor.process('large_feed.csv'):
    print(f"Processed batch: {batch_results.records_processed}")
```

---

## API Reference

### Core Classes

#### ProductFeedValidator

```python
class ProductFeedValidator:
    def __init__(self, config=None, custom_rules=None):
        """Initialize validator with optional config and rules"""
        
    def validate_file(self, filepath, format=None):
        """Validate a feed file"""
        
    def validate_data(self, data, format='json'):
        """Validate data structure directly"""
        
    def get_validation_report(self):
        """Get detailed validation report"""
```

#### ValidationResults

```python
class ValidationResults:
    valid_count: int
    error_count: int
    warning_count: int
    score: float  # Percentage
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    metadata: Dict
```

### Validation Methods

| Method | Description | Parameters |
|--------|-------------|-----------|
| `validate_file()` | Validate file | filepath, format |
| `validate_data()` | Validate data dict | data, format |
| `validate_row()` | Validate single row | row_data |
| `check_duplicates()` | Find duplicates | data, key_field |
| `get_statistics()` | Get feed statistics | - |

---

## Feed Format Specifications

### CSV Format
```csv
product_id,product_name,price,availability,category
P001,Widget A,19.99,in_stock,Electronics
P002,Widget B,29.99,out_of_stock,Electronics
P003,Gadget X,49.99,in_stock,Accessories
```

**Requirements:**
- Header row required
- UTF-8 encoding
- Standard CSV escaping for special characters

### XML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed>
  <product>
    <product_id>P001</product_id>
    <product_name>Widget A</product_name>
    <price currency="USD">19.99</price>
    <availability>in_stock</availability>
  </product>
</feed>
```

### JSON Format
```json
{
  "products": [
    {
      "product_id": "P001",
      "product_name": "Widget A",
      "price": 19.99,
      "availability": "in_stock"
    }
  ]
}
```

---

## Validation Rules

### Default Rules

#### Required Field Validation
- All specified required fields must be present
- Fields cannot be null or empty
- Field data types must match specifications

#### Data Type Validation
- Numeric fields: Must contain valid numbers
- Currency: Valid format with 2 decimal places
- Dates: Must be ISO 8601 format (YYYY-MM-DD)
- URLs: Must be valid HTTP/HTTPS URLs
- Email: Must follow RFC 5322 standards

#### Business Rules
- Product IDs: Must be unique
- Prices: Must be greater than 0
- Stock quantities: Must be non-negative integers
- Availability: Must be from allowed values (in_stock, out_of_stock, pre_order)

### Error Severity Levels

| Level | Impact | Example |
|-------|--------|---------|
| Critical | Record unusable | Missing product_id |
| Warning | Data quality issue | Unusually high price |
| Info | Minor issue | Optional field empty |

---

## Error Handling

### Common Errors and Solutions

#### FileNotFoundError
```python
try:
    results = validator.validate_file('nonexistent.csv')
except FileNotFoundError:
    print("Feed file not found. Check the file path.")
```

#### InvalidFormatError
```python
# Always specify format for clarity
results = validator.validate_file('data.csv', format='csv')
```

#### ValidationError Details
```python
results = validator.validate_file('products.json')

if results.error_count > 0:
    for error in results.errors:
        print(f"Error at row {error['row']}: {error['message']}")
        print(f"Severity: {error['severity']}")
        print(f"Field: {error['field']}")
```

---

## Performance Optimization

### Tips for Large Files

1. **Chunked Processing**
   ```python
   processor = FeedProcessor(chunk_size=50000)
   for batch in processor.process('large_feed.csv'):
       # Process batch
       pass
   ```

2. **Parallel Validation**
   ```python
   validator = ProductFeedValidator(workers=4)
   results = validator.validate_file('products.csv')
   ```

3. **Caching**
   ```python
   validator = ProductFeedValidator(enable_cache=True)
   # Subsequent validations use cache
   ```

4. **Index Creation**
   ```python
   # Create indexes on frequently searched fields
   validator.create_index('product_id')
   ```

### Benchmarks

| File Size | Records | Processing Time |
|-----------|---------|-----------------|
| 10 MB | ~50K | ~2 seconds |
| 100 MB | ~500K | ~15 seconds |
| 1 GB | ~5M | ~2 minutes |

---

## Troubleshooting

### Common Issues

#### Issue: Slow Validation Performance
**Solution:** 
- Enable chunked processing
- Increase worker count
- Check available system memory
- Profile the validation rules

#### Issue: Memory Exhaustion
**Solution:**
- Reduce chunk size
- Enable streaming mode
- Process in batches
- Monitor with `memory_profiler`

#### Issue: Encoding Errors
**Solution:**
- Ensure UTF-8 encoding: `iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv`
- Specify encoding explicitly in config
- Check for BOM markers

#### Issue: Rule Conflicts
**Solution:**
- Review custom rule definitions
- Check rule execution order
- Test rules individually
- Use validation logs for debugging

### Debug Mode

```bash
python -m feedvalidator validate --file products.csv --debug --verbose
```

---

## Contributing

### Development Setup
```bash
git clone https://github.com/deepakgargct/productfeedreview.git
cd productfeedreview
pip install -r requirements-dev.txt
```

### Running Tests
```bash
pytest tests/ -v
pytest tests/ --cov=feedvalidator
```

### Code Standards
- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation

### Submission Process
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit pull request

---

## FAQ

### Q: What file formats are supported?
**A:** CSV, XML, and JSON formats are fully supported. Other formats can be added through custom parsers.

### Q: Can I validate feeds in real-time?
**A:** Yes, use the API endpoints or the Python API for programmatic validation.

### Q: How do I define custom validation rules?
**A:** Create a JSON rules file or use the CustomRules class in Python.

### Q: What's the maximum file size?
**A:** Default is 500MB, configurable in settings. For larger files, use batch processing.

### Q: Is there a web interface?
**A:** Currently CLI and API only. Web interface roadmap is in progress.

### Q: How are results stored?
**A:** Results can be exported as JSON, CSV, or HTML. Database integration available.

### Q: Can I schedule automatic validations?
**A:** Yes, integrate with cron jobs or use the task scheduler module.

### Q: How do I handle private/sensitive data?
**A:** Use the sanitization features and configure field masking in settings.

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Contact the development team

---

**Last Updated:** January 6, 2026  
**Version:** 1.0.0

