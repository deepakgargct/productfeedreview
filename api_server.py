"""
Flask API Server with Validation Endpoints
Provides endpoints for product feed review validation
"""

from flask import Flask, request, jsonify
from datetime import datetime
import re
from typing import Dict, List, Tuple

app = Flask(__name__)

# Configuration
app.config['JSON_SORT_KEYS'] = False


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class FeedValidator:
    """Validator class for product feed data"""
    
    @staticmethod
    def validate_product_id(product_id: str) -> bool:
        """Validate product ID format"""
        if not product_id or not isinstance(product_id, str):
            return False
        return len(product_id) > 0 and len(product_id) <= 100
    
    @staticmethod
    def validate_product_name(name: str) -> bool:
        """Validate product name"""
        if not name or not isinstance(name, str):
            return False
        return 1 <= len(name) <= 500
    
    @staticmethod
    def validate_price(price) -> bool:
        """Validate price format and value"""
        try:
            price_float = float(price)
            return price_float >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            return False
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, url))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_feed_item(item: Dict) -> Tuple[bool, List[str]]:
        """Validate a feed item and return validation status and error list"""
        errors = []
        
        # Required fields validation
        if 'product_id' not in item:
            errors.append("Missing required field: product_id")
        elif not FeedValidator.validate_product_id(item['product_id']):
            errors.append("Invalid product_id format")
        
        if 'product_name' not in item:
            errors.append("Missing required field: product_name")
        elif not FeedValidator.validate_product_name(item['product_name']):
            errors.append("Invalid product_name format")
        
        if 'price' not in item:
            errors.append("Missing required field: price")
        elif not FeedValidator.validate_price(item['price']):
            errors.append("Invalid price format")
        
        # Optional fields validation
        if 'url' in item and not FeedValidator.validate_url(item['url']):
            errors.append("Invalid product URL format")
        
        if 'contact_email' in item and not FeedValidator.validate_email(item['contact_email']):
            errors.append("Invalid contact email format")
        
        return len(errors) == 0, errors


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'service': 'Product Feed Review API'
    }), 200


@app.route('/api/validate/product', methods=['POST'])
def validate_product():
    """
    Validate a single product item
    
    Expected JSON payload:
    {
        "product_id": "string",
        "product_name": "string",
        "price": number,
        "url": "string (optional)",
        "contact_email": "string (optional)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'valid': False,
                'errors': ['No JSON data provided']
            }), 400
        
        is_valid, errors = FeedValidator.validate_feed_item(data)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


@app.route('/api/validate/feed', methods=['POST'])
def validate_feed():
    """
    Validate a complete product feed (batch validation)
    
    Expected JSON payload:
    {
        "products": [
            {
                "product_id": "string",
                "product_name": "string",
                "price": number,
                "url": "string (optional)",
                "contact_email": "string (optional)"
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'products' not in data:
            return jsonify({
                'valid': False,
                'error': 'Missing "products" field in request'
            }), 400
        
        products = data['products']
        
        if not isinstance(products, list):
            return jsonify({
                'valid': False,
                'error': '"products" must be a list'
            }), 400
        
        results = []
        total_valid = 0
        total_invalid = 0
        
        for idx, product in enumerate(products):
            is_valid, errors = FeedValidator.validate_feed_item(product)
            
            results.append({
                'index': idx,
                'product_id': product.get('product_id', 'N/A'),
                'valid': is_valid,
                'errors': errors
            })
            
            if is_valid:
                total_valid += 1
            else:
                total_invalid += 1
        
        return jsonify({
            'summary': {
                'total_items': len(products),
                'valid_items': total_valid,
                'invalid_items': total_invalid,
                'validation_passed': total_invalid == 0
            },
            'results': results,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


@app.route('/api/validate/field/<field_type>', methods=['POST'])
def validate_field(field_type):
    """
    Validate a specific field type
    
    Supported field_types: product_id, product_name, price, url, email
    Expected JSON payload:
    {
        "value": "value to validate"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({
                'valid': False,
                'error': 'Missing "value" field in request'
            }), 400
        
        value = data['value']
        validators = {
            'product_id': FeedValidator.validate_product_id,
            'product_name': FeedValidator.validate_product_name,
            'price': FeedValidator.validate_price,
            'url': FeedValidator.validate_url,
            'email': FeedValidator.validate_email
        }
        
        if field_type not in validators:
            return jsonify({
                'valid': False,
                'error': f'Unknown field type: {field_type}. Supported types: {", ".join(validators.keys())}'
            }), 400
        
        validator = validators[field_type]
        is_valid = validator(value)
        
        return jsonify({
            'field_type': field_type,
            'valid': is_valid,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


@app.route('/api/info', methods=['GET'])
def api_info():
    """Get information about available API endpoints"""
    return jsonify({
        'service': 'Product Feed Review API',
        'version': '1.0.0',
        'endpoints': {
            'GET /health': 'Health check endpoint',
            'GET /api/info': 'API information',
            'POST /api/validate/product': 'Validate a single product',
            'POST /api/validate/feed': 'Batch validate multiple products',
            'POST /api/validate/field/<field_type>': 'Validate a specific field type'
        },
        'supported_field_types': ['product_id', 'product_name', 'price', 'url', 'email'],
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'path': request.path,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
