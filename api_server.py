"""
Flask API Server with Validation Endpoints
Provides endpoints for product feed review validation with compliance scoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import io
import json
from chatgpt_feed_validator import ChatGPTFeedValidator, ValidationResult, ValidationLevel

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def calculate_compliance_score(validation_result: ValidationResult) -> dict:
    """
    Calculate compliance score and categorize issues
    
    Returns:
        dict with compliance_score, critical_issues, warnings, recommendations
    """
    # Categorize issues by severity
    critical_issues = []
    warnings = []
    recommendations = []
    
    for issue in validation_result.issues:
        critical_issues.append({
            'field': issue.field,
            'message': issue.message,
            'suggestion': issue.suggestion,
            'severity': 'CRITICAL'
        })
    
    for warning in validation_result.warnings:
        # Determine if this is a recommendation or warning
        if warning.level == ValidationLevel.INFO:
            recommendations.append({
                'field': warning.field,
                'message': warning.message,
                'suggestion': warning.suggestion,
                'action': warning.suggestion or f"Add {warning.field} for better compliance"
            })
        else:
            warnings.append({
                'field': warning.field,
                'message': warning.message,
                'suggestion': warning.suggestion,
                'severity': 'WARNING'
            })
    
    return {
        'compliance_score': round(validation_result.score, 2),
        'compliance_percentage': f"{round(validation_result.score, 1)}%",
        'critical_issues': critical_issues,
        'warnings': warnings,
        'recommendations': recommendations,
        'is_compliant': validation_result.is_valid,
        'total_issues': len(critical_issues),
        'total_warnings': len(warnings),
        'total_recommendations': len(recommendations)
    }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'service': 'Product Feed Review API',
        'version': '2.0'
    }), 200


@app.route('/api/validate', methods=['POST'])
def validate_product():
    """
    Validate a single product with compliance scoring
    
    Expected JSON payload:
    {
        "product_id": "string",
        "title": "string",
        "description": "string",
        "price": number,
        "currency": "string",
        "category": "string",
        "availability": "string",
        ...
    }
    
    Returns:
        Compliance score, critical issues, warnings, and recommendations
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'compliance_score': 0
            }), 400
        
        # Create validator instance
        validator = ChatGPTFeedValidator(strict_mode=False)
        
        # Validate the product
        result = validator.validate_product(data)
        
        # Calculate compliance score and categorize issues
        compliance_data = calculate_compliance_score(result)
        
        return jsonify({
            'product_id': result.product_id,
            'valid': result.is_valid,
            'compliance_score': compliance_data['compliance_score'],
            'compliance_percentage': compliance_data['compliance_percentage'],
            'is_compliant': compliance_data['is_compliant'],
            'critical_issues': compliance_data['critical_issues'],
            'warnings': compliance_data['warnings'],
            'recommendations': compliance_data['recommendations'],
            'summary': {
                'total_critical': compliance_data['total_issues'],
                'total_warnings': compliance_data['total_warnings'],
                'total_recommendations': compliance_data['total_recommendations']
            },
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Validation error: {str(e)}',
            'compliance_score': 0,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


@app.route('/api/validate-feed', methods=['POST'])
def validate_feed():
    """
    Validate batch CSV/JSON product feed with compliance scoring
    
    Accepts:
    - JSON array of products
    - CSV file upload (multipart/form-data)
    - JSON file upload (multipart/form-data)
    
    Returns:
        Batch validation results with compliance summary
    """
    try:
        products = []
        
        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Read file based on extension
            if file.filename.endswith('.csv'):
                # Parse CSV
                df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
                products = df.to_dict('records')
            elif file.filename.endswith('.json'):
                # Parse JSON
                content = file.read().decode('utf-8')
                data = json.loads(content)
                if isinstance(data, list):
                    products = data
                elif isinstance(data, dict) and 'products' in data:
                    products = data['products']
                else:
                    products = [data]
            else:
                return jsonify({'error': 'Unsupported file format. Use CSV or JSON'}), 400
        
        # Check if it's JSON in request body
        elif request.is_json:
            data = request.get_json()
            
            if isinstance(data, list):
                products = data
            elif isinstance(data, dict):
                if 'products' in data:
                    products = data['products']
                else:
                    # Single product
                    products = [data]
            else:
                return jsonify({'error': 'Invalid JSON format'}), 400
        else:
            return jsonify({'error': 'No data provided. Send JSON or upload CSV/JSON file'}), 400
        
        if not products:
            return jsonify({'error': 'No products found in the feed'}), 400
        
        # Validate all products
        validator = ChatGPTFeedValidator(strict_mode=False)
        feed_results = validator.validate_feed(products)
        
        # Calculate compliance for each product
        detailed_results = []
        total_compliance = 0
        total_critical = 0
        total_warnings = 0
        total_recommendations = 0
        compliant_count = 0
        
        for product_result in validator.validation_results:
            compliance_data = calculate_compliance_score(product_result)
            
            detailed_results.append({
                'product_id': product_result.product_id,
                'valid': product_result.is_valid,
                'compliance_score': compliance_data['compliance_score'],
                'compliance_percentage': compliance_data['compliance_percentage'],
                'critical_issues': compliance_data['critical_issues'],
                'warnings': compliance_data['warnings'],
                'recommendations': compliance_data['recommendations'],
                'summary': {
                    'total_critical': compliance_data['total_issues'],
                    'total_warnings': compliance_data['total_warnings'],
                    'total_recommendations': compliance_data['total_recommendations']
                }
            })
            
            total_compliance += compliance_data['compliance_score']
            total_critical += compliance_data['total_issues']
            total_warnings += compliance_data['total_warnings']
            total_recommendations += compliance_data['total_recommendations']
            
            if product_result.is_valid:
                compliant_count += 1
        
        # Calculate overall compliance
        avg_compliance = total_compliance / len(products) if products else 0
        compliance_rate = (compliant_count / len(products) * 100) if products else 0
        
        return jsonify({
            'batch_summary': {
                'total_products': len(products),
                'compliant_products': compliant_count,
                'non_compliant_products': len(products) - compliant_count,
                'compliance_rate': f"{round(compliance_rate, 1)}%",
                'average_compliance_score': round(avg_compliance, 2),
                'total_critical_issues': total_critical,
                'total_warnings': total_warnings,
                'total_recommendations': total_recommendations
            },
            'products': detailed_results,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Feed validation error: {str(e)}',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


@app.route('/api/info', methods=['GET'])
def api_info():
    """Get information about available API endpoints"""
    return jsonify({
        'service': 'Product Feed Review API',
        'version': '2.0.0',
        'endpoints': {
            'GET /health': 'Health check endpoint',
            'GET /api/info': 'API information',
            'POST /api/validate': 'Validate a single product with compliance scoring',
            'POST /api/validate-feed': 'Batch validate CSV/JSON product feeds'
        },
        'features': [
            'ChatGPT Product Specification compliance',
            'Compliance score (0-100%)',
            'Critical issue identification',
            'Actionable recommendations',
            'CSV and JSON batch processing',
            'Detailed validation reports'
        ],
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

