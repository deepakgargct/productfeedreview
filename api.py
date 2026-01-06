"""
Flask-based REST API for Product Feed Review and Validation
Provides endpoints for product data validation, feed processing, and quality checks
"""

from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions & Decorators
# ============================================================================

def validate_json_request(f):
    """Decorator to validate JSON request content-type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function


def validate_product_data(product_data):
    """
    Validate product data structure and required fields
    
    Args:
        product_data (dict): Product information to validate
        
    Returns:
        tuple: (is_valid, errors_list)
    """
    required_fields = ['name', 'sku', 'price', 'description']
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in product_data:
            errors.append(f"Missing required field: {field}")
        elif not product_data[field]:
            errors.append(f"Field '{field}' cannot be empty")
    
    # Validate price format
    if 'price' in product_data:
        try:
            price = float(product_data['price'])
            if price < 0:
                errors.append("Price cannot be negative")
        except (ValueError, TypeError):
            errors.append("Price must be a valid number")
    
    # Validate SKU format (alphanumeric, no special chars)
    if 'sku' in product_data:
        sku = str(product_data['sku']).strip()
        if not sku.isalnum():
            errors.append("SKU must contain only alphanumeric characters")
        if len(sku) < 3:
            errors.append("SKU must be at least 3 characters long")
    
    # Validate description length
    if 'description' in product_data:
        desc = str(product_data['description']).strip()
        if len(desc) < 10:
            errors.append("Description must be at least 10 characters long")
    
    return len(errors) == 0, errors


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Product Feed Review API'
    }), 200


@app.route('/api/status', methods=['GET'])
def api_status():
    """Get API status and version information"""
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ============================================================================
# Product Validation Endpoints
# ============================================================================

@app.route('/api/validate/product', methods=['POST'])
@validate_json_request
def validate_product():
    """
    Validate a single product
    
    Request body:
    {
        "name": "Product Name",
        "sku": "SKU123",
        "price": 29.99,
        "description": "Product description text here",
        "category": "Electronics",
        "quantity": 100
    }
    
    Returns:
    {
        "valid": true/false,
        "errors": [],
        "warnings": [],
        "product": {...},
        "timestamp": "2026-01-06T13:06:56"
    }
    """
    try:
        product_data = request.get_json()
        
        if not product_data:
            return jsonify({'error': 'Empty request body'}), 400
        
        is_valid, errors = validate_product_data(product_data)
        
        response = {
            'valid': is_valid,
            'errors': errors,
            'warnings': [],
            'product': product_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add warnings for optional fields
        if 'quantity' in product_data and product_data['quantity'] < 10:
            response['warnings'].append('Low stock quantity detected')
        
        status_code = 200 if is_valid else 400
        logger.info(f"Product validation - Valid: {is_valid}, SKU: {product_data.get('sku', 'N/A')}")
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Error validating product: {str(e)}")
        return jsonify({'error': f'Validation error: {str(e)}'}), 500


@app.route('/api/validate/batch', methods=['POST'])
@validate_json_request
def validate_batch_products():
    """
    Validate multiple products in a batch
    
    Request body:
    {
        "products": [
            {"name": "Product 1", "sku": "SKU001", "price": 10.00, "description": "..."},
            {"name": "Product 2", "sku": "SKU002", "price": 20.00, "description": "..."}
        ]
    }
    
    Returns:
    {
        "total": 2,
        "valid_count": 1,
        "invalid_count": 1,
        "results": [
            {"sku": "SKU001", "valid": true, "errors": []},
            {"sku": "SKU002", "valid": false, "errors": [...]}
        ],
        "timestamp": "2026-01-06T13:06:56"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'products' not in data:
            return jsonify({'error': 'Missing "products" field in request body'}), 400
        
        products = data['products']
        if not isinstance(products, list):
            return jsonify({'error': '"products" must be a list'}), 400
        
        results = []
        valid_count = 0
        invalid_count = 0
        
        for product in products:
            is_valid, errors = validate_product_data(product)
            
            result = {
                'sku': product.get('sku', 'N/A'),
                'name': product.get('name', 'N/A'),
                'valid': is_valid,
                'errors': errors
            }
            results.append(result)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
        
        response = {
            'total': len(products),
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Batch validation - Total: {len(products)}, Valid: {valid_count}, Invalid: {invalid_count}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error validating batch: {str(e)}")
        return jsonify({'error': f'Batch validation error: {str(e)}'}), 500


# ============================================================================
# Feed Processing Endpoints
# ============================================================================

@app.route('/api/feed/analyze', methods=['POST'])
@validate_json_request
def analyze_feed():
    """
    Analyze product feed quality and completeness
    
    Request body:
    {
        "feed_name": "Feed Name",
        "feed_data": [...]
    }
    
    Returns quality metrics and improvement suggestions
    """
    try:
        data = request.get_json()
        
        if not data or 'feed_data' not in data:
            return jsonify({'error': 'Missing "feed_data" field'}), 400
        
        feed_data = data['feed_data']
        feed_name = data.get('feed_name', 'Unnamed Feed')
        
        if not isinstance(feed_data, list):
            return jsonify({'error': '"feed_data" must be a list'}), 400
        
        total_products = len(feed_data)
        valid_products = 0
        quality_score = 0
        issues = []
        
        for product in feed_data:
            is_valid, _ = validate_product_data(product)
            if is_valid:
                valid_products += 1
        
        # Calculate quality score (0-100)
        quality_score = int((valid_products / total_products * 100)) if total_products > 0 else 0
        
        if quality_score < 80:
            issues.append("Feed quality is below 80% threshold")
        
        if total_products == 0:
            issues.append("Feed is empty")
        
        response = {
            'feed_name': feed_name,
            'total_products': total_products,
            'valid_products': valid_products,
            'invalid_products': total_products - valid_products,
            'quality_score': quality_score,
            'issues': issues,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Feed analysis - Name: {feed_name}, Quality Score: {quality_score}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error analyzing feed: {str(e)}")
        return jsonify({'error': f'Feed analysis error: {str(e)}'}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
