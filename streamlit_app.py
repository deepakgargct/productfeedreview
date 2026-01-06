"""
ChatGPT Product Feed Schema Validator
A comprehensive Streamlit application for validating product feed schemas,
providing recommendations, and generating detailed validation reports.
"""

import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime
from typing import Dict, List, Tuple, Any
import re

# Set page configuration
st.set_page_config(
    page_title="Product Feed Schema Validator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Define schema requirements
REQUIRED_FIELDS = {
    'id': {'type': 'string', 'description': 'Unique product identifier'},
    'title': {'type': 'string', 'description': 'Product title', 'max_length': 150},
    'description': {'type': 'string', 'description': 'Product description'},
    'price': {'type': 'float', 'description': 'Product price'},
    'currency': {'type': 'string', 'description': 'Currency code (e.g., USD, EUR)'},
    'availability': {'type': 'string', 'description': 'Availability status'},
    'image_link': {'type': 'string', 'description': 'Product image URL'},
    'link': {'type': 'string', 'description': 'Product landing page URL'},
}

OPTIONAL_FIELDS = {
    'category': {'type': 'string', 'description': 'Product category'},
    'brand': {'type': 'string', 'description': 'Product brand'},
    'condition': {'type': 'string', 'description': 'Product condition (new/used/refurbished)'},
    'sku': {'type': 'string', 'description': 'Product SKU'},
    'gtin': {'type': 'string', 'description': 'Global Trade Item Number'},
    'shipping': {'type': 'string', 'description': 'Shipping information'},
    'sale_price': {'type': 'float', 'description': 'Sale price if applicable'},
    'rating': {'type': 'float', 'description': 'Product rating (0-5)'},
    'reviews_count': {'type': 'integer', 'description': 'Number of reviews'},
}

class ProductFeedValidator:
    """Validates product feed schema and generates recommendations."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.recommendations = []
        self.valid_products = 0
        self.invalid_products = 0
    
    def validate_product(self, product: Dict, product_index: int) -> Dict:
        """Validate a single product against the schema."""
        issues = {
            'index': product_index,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check required fields
        for field, schema in REQUIRED_FIELDS.items():
            if field not in product or product[field] is None:
                issues['errors'].append(f"Missing required field: {field}")
            else:
                # Type validation
                value = product[field]
                field_type = schema.get('type', 'string')
                
                if field_type == 'float':
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        issues['errors'].append(f"Field '{field}' must be a valid number, got: {value}")
                
                elif field_type == 'integer':
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        issues['errors'].append(f"Field '{field}' must be an integer, got: {value}")
                
                # Length validation
                if field == 'title' and len(str(value)) > schema.get('max_length', 999):
                    issues['warnings'].append(f"Field '{field}' exceeds recommended length of {schema.get('max_length')}")
        
        # Validate optional fields
        for field, schema in OPTIONAL_FIELDS.items():
            if field in product and product[field] is not None:
                value = product[field]
                field_type = schema.get('type', 'string')
                
                if field_type == 'float':
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        issues['warnings'].append(f"Field '{field}' should be a valid number")
        
        # URL validation
        for url_field in ['image_link', 'link']:
            if url_field in product:
                if not self._is_valid_url(str(product[url_field])):
                    issues['warnings'].append(f"Field '{field}' appears to be an invalid URL")
        
        # Additional validations
        if 'price' in product and 'sale_price' in product:
            try:
                price = float(product['price'])
                sale_price = float(product['sale_price'])
                if sale_price >= price:
                    issues['recommendations'].append("Sale price should be lower than regular price")
            except (ValueError, TypeError):
                pass
        
        # Rating validation
        if 'rating' in product:
            try:
                rating = float(product['rating'])
                if not (0 <= rating <= 5):
                    issues['warnings'].append("Rating should be between 0 and 5")
            except (ValueError, TypeError):
                pass
        
        # Recommendations
        missing_optional = [f for f in OPTIONAL_FIELDS.keys() if f not in product]
        if missing_optional:
            issues['recommendations'].append(f"Consider adding optional fields: {', '.join(missing_optional[:3])}")
        
        if 'description' in product:
            desc_len = len(str(product['description']))
            if desc_len < 50:
                issues['recommendations'].append("Product description is quite short. Consider adding more details.")
            elif desc_len > 5000:
                issues['recommendations'].append("Product description is very long. Consider making it more concise.")
        
        return issues
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        url_pattern = re.compile(
            r'^https?://',
            re.IGNORECASE
        )
        return bool(url_pattern.match(url))
    
    def validate_feed(self, products: List[Dict]) -> Dict:
        """Validate entire product feed."""
        results = {
            'products': [],
            'summary': {},
            'overall_health': 'GOOD'
        }
        
        for idx, product in enumerate(products):
            result = self.validate_product(product, idx)
            results['products'].append(result)
            
            if result['errors']:
                self.invalid_products += 1
            else:
                self.valid_products += 1
        
        # Generate summary
        total_products = len(products)
        total_errors = sum(len(p['errors']) for p in results['products'])
        total_warnings = sum(len(p['warnings']) for p in results['products'])
        
        results['summary'] = {
            'total_products': total_products,
            'valid_products': self.valid_products,
            'invalid_products': self.invalid_products,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'error_rate': (self.invalid_products / total_products * 100) if total_products > 0 else 0
        }
        
        # Determine overall health
        error_rate = results['summary']['error_rate']
        if error_rate == 0:
            results['overall_health'] = 'EXCELLENT'
        elif error_rate < 5:
            results['overall_health'] = 'GOOD'
        elif error_rate < 20:
            results['overall_health'] = 'FAIR'
        else:
            results['overall_health'] = 'POOR'
        
        return results

def load_sample_data() -> str:
    """Return sample product feed JSON."""
    sample_data = [
        {
            "id": "PROD001",
            "title": "Premium Wireless Headphones",
            "description": "High-quality wireless headphones with active noise cancellation and 30-hour battery life",
            "price": 199.99,
            "currency": "USD",
            "availability": "in stock",
            "image_link": "https://example.com/headphones.jpg",
            "link": "https://example.com/products/headphones",
            "category": "Electronics > Audio",
            "brand": "AudioPro",
            "condition": "new",
            "sku": "AP-WH001",
            "rating": 4.5,
            "reviews_count": 234
        },
        {
            "id": "PROD002",
            "title": "USB-C Cable",
            "description": "Durable USB-C charging cable",
            "price": 15.99,
            "currency": "USD",
            "availability": "in stock",
            "image_link": "https://example.com/cable.jpg",
            "link": "https://example.com/products/cable",
            "brand": "TechCables"
        }
    ]
    return json.dumps(sample_data, indent=2)

def generate_report(validation_results: Dict) -> str:
    """Generate a detailed text report."""
    report = []
    report.append("=" * 80)
    report.append("PRODUCT FEED VALIDATION REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Summary
    summary = validation_results['summary']
    report.append("VALIDATION SUMMARY")
    report.append("-" * 80)
    report.append(f"Overall Health:        {validation_results['overall_health']}")
    report.append(f"Total Products:        {summary['total_products']}")
    report.append(f"Valid Products:        {summary['valid_products']} ✓")
    report.append(f"Invalid Products:      {summary['invalid_products']} ✗")
    report.append(f"Total Errors:          {summary['total_errors']}")
    report.append(f"Total Warnings:        {summary['total_warnings']}")
    report.append(f"Error Rate:            {summary['error_rate']:.2f}%\n")
    
    # Details for problematic products
    problematic = [p for p in validation_results['products'] if p['errors'] or p['warnings']]
    if problematic:
        report.append("DETAILED FINDINGS")
        report.append("-" * 80)
        for product in problematic[:10]:  # Limit to first 10
            report.append(f"\nProduct #{product['index'] + 1}:")
            if product['errors']:
                for error in product['errors']:
                    report.append(f"  ✗ ERROR: {error}")
            if product['warnings']:
                for warning in product['warnings']:
                    report.append(f"  ⚠ WARNING: {warning}")
            if product['recommendations']:
                for rec in product['recommendations']:
                    report.append(f"  → RECOMMENDATION: {rec}")
    
    report.append("\n" + "=" * 80)
    return "\n".join(report)

def main():
    # Header
    st.markdown("# 🔍 Product Feed Schema Validator")
    st.markdown("Validate product feed schemas, identify issues, and get recommendations for improvement")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio(
            "Select a page:",
            ["Validation", "Schema Reference", "Best Practices", "About"]
        )
    
    if page == "Validation":
        validation_page()
    elif page == "Schema Reference":
        schema_reference_page()
    elif page == "Best Practices":
        best_practices_page()
    else:
        about_page()

def validation_page():
    """Main validation page."""
    st.markdown("## 📋 Feed Validation")
    
    # Input method selection
    col1, col2, col3 = st.columns(3)
    with col1:
        input_method = st.radio("Select input method:", ["Paste JSON", "Upload File", "Sample Data"])
    
    feed_data = None
    
    if input_method == "Paste JSON":
        st.markdown("### Paste your product feed JSON")
        json_input = st.text_area(
            "Enter JSON:",
            height=300,
            placeholder='[{"id": "1", "title": "Product", ...}]'
        )
        if json_input:
            try:
                feed_data = json.loads(json_input)
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")
    
    elif input_method == "Upload File":
        st.markdown("### Upload your product feed file")
        uploaded_file = st.file_uploader("Choose a JSON or CSV file", type=['json', 'csv'])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.json'):
                    feed_data = json.load(uploaded_file)
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    feed_data = df.to_dict('records')
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
    
    else:  # Sample Data
        st.markdown("### Using sample product feed")
        if st.button("Load Sample Data"):
            sample_json = load_sample_data()
            feed_data = json.loads(sample_json)
            st.success("✓ Sample data loaded")
        st.info("This sample data demonstrates the schema with valid and invalid entries")
        with st.expander("View Sample Data"):
            st.code(load_sample_data(), language="json")
    
    # Validation
    if feed_data:
        if st.button("▶ Run Validation", use_container_width=True, type="primary"):
            with st.spinner("Validating feed..."):
                validator = ProductFeedValidator()
                results = validator.validate_feed(feed_data if isinstance(feed_data, list) else [feed_data])
            
            # Display results
            display_validation_results(results)
    
    # Output options
    if feed_data:
        st.markdown("---")
        st.markdown("### 📊 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Download Report (TXT)", use_container_width=True):
                validator = ProductFeedValidator()
                results = validator.validate_feed(feed_data if isinstance(feed_data, list) else [feed_data])
                report = generate_report(results)
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("📊 Export as CSV", use_container_width=True):
                validator = ProductFeedValidator()
                results = validator.validate_feed(feed_data if isinstance(feed_data, list) else [feed_data])
                csv_data = convert_results_to_csv(results)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("📋 Export as JSON", use_container_width=True):
                validator = ProductFeedValidator()
                results = validator.validate_feed(feed_data if isinstance(feed_data, list) else [feed_data])
                json_data = json.dumps(results, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

def display_validation_results(results: Dict):
    """Display validation results with visualizations."""
    st.markdown("---")
    st.markdown("## ✅ Validation Results")
    
    # Health Status
    summary = results['summary']
    health = results['overall_health']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Feed Health", health, delta="Overall Status")
    with col2:
        st.metric("Valid Products", f"{summary['valid_products']}/{summary['total_products']}")
    with col3:
        st.metric("Error Rate", f"{summary['error_rate']:.1f}%")
    with col4:
        st.metric("Total Errors", summary['total_errors'])
    with col5:
        st.metric("Total Warnings", summary['total_warnings'])
    
    # Health color coding
    if health == 'EXCELLENT':
        st.markdown('<div class="success-box">✓ Your feed is in excellent condition!</div>', unsafe_allow_html=True)
    elif health == 'GOOD':
        st.markdown('<div class="success-box">✓ Your feed is in good condition with minor issues to address</div>', unsafe_allow_html=True)
    elif health == 'FAIR':
        st.markdown('<div class="warning-box">⚠ Your feed has several issues that should be addressed</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">✗ Your feed has critical issues that need attention</div>', unsafe_allow_html=True)
    
    # Detailed Results
    st.markdown("### 📊 Detailed Analysis")
    
    # Products with errors/warnings
    problematic = [p for p in results['products'] if p['errors'] or p['warnings'] or p['recommendations']]
    
    if problematic:
        st.markdown(f"**Products with issues:** {len(problematic)}")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Errors", "Warnings & Recommendations", "Summary Table"])
        
        with tab1:
            error_products = [p for p in problematic if p['errors']]
            if error_products:
                for product in error_products[:10]:
                    with st.expander(f"Product #{product['index'] + 1} - {len(product['errors'])} errors"):
                        for error in product['errors']:
                            st.error(f"• {error}")
            else:
                st.success("No errors found!")
        
        with tab2:
            for product in problematic[:10]:
                if product['warnings'] or product['recommendations']:
                    with st.expander(f"Product #{product['index'] + 1}"):
                        if product['warnings']:
                            st.warning("**Warnings:**")
                            for warning in product['warnings']:
                                st.write(f"• {warning}")
                        if product['recommendations']:
                            st.info("**Recommendations:**")
                            for rec in product['recommendations']:
                                st.write(f"• {rec}")
        
        with tab3:
            summary_data = []
            for product in results['products']:
                summary_data.append({
                    'Product #': product['index'] + 1,
                    'Errors': len(product['errors']),
                    'Warnings': len(product['warnings']),
                    'Recommendations': len(product['recommendations']),
                    'Status': '✗ Invalid' if product['errors'] else '✓ Valid'
                })
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
    else:
        st.success("✓ All products passed validation!")

def convert_results_to_csv(results: Dict) -> str:
    """Convert validation results to CSV format."""
    data = []
    for product in results['products']:
        data.append({
            'Product #': product['index'] + 1,
            'Errors': len(product['errors']),
            'Warnings': len(product['warnings']),
            'Recommendations': len(product['recommendations']),
            'Error Details': ' | '.join(product['errors']) if product['errors'] else 'None',
            'Warning Details': ' | '.join(product['warnings']) if product['warnings'] else 'None',
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def schema_reference_page():
    """Schema reference documentation page."""
    st.markdown("## 📚 Schema Reference")
    st.markdown("Complete documentation of required and optional fields for product feeds")
    
    st.markdown("### ✓ Required Fields")
    st.markdown("These fields must be present in every product:")
    
    required_df = pd.DataFrame([
        {
            'Field': field,
            'Type': info['type'],
            'Description': info['description']
        }
        for field, info in REQUIRED_FIELDS.items()
    ])
    st.dataframe(required_df, use_container_width=True, hide_index=True)
    
    st.markdown("### 🔹 Optional Fields (Recommended)")
    st.markdown("These fields are optional but highly recommended for better feed quality:")
    
    optional_df = pd.DataFrame([
        {
            'Field': field,
            'Type': info['type'],
            'Description': info['description']
        }
        for field, info in OPTIONAL_FIELDS.items()
    ])
    st.dataframe(optional_df, use_container_width=True, hide_index=True)
    
    st.markdown("### 📋 Valid Values")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Availability Values:**")
        st.code("in stock, out of stock, preorder, discontinued")
    
    with col2:
        st.markdown("**Condition Values:**")
        st.code("new, used, refurbished")
    
    st.markdown("**Currency Codes (ISO 4217):**")
    st.code("USD, EUR, GBP, JPY, CAD, AUD, INR, etc.")

def best_practices_page():
    """Best practices documentation page."""
    st.markdown("## 💡 Best Practices")
    
    practices = {
        "Product Titles": [
            "Keep titles under 150 characters",
            "Be specific and descriptive",
            "Include key attributes (brand, model, size)",
            "Avoid special characters and excessive capitalization",
            "Don't include price or currency in the title"
        ],
        "Descriptions": [
            "Write at least 50 characters",
            "Include key features and benefits",
            "Use proper grammar and formatting",
            "Highlight unique selling points",
            "Keep descriptions under 5000 characters"
        ],
        "Pricing": [
            "Always include the base price",
            "Use valid currency codes",
            "Sale price should be lower than regular price",
            "Include shipping costs if applicable",
            "Update prices regularly to avoid stale data"
        ],
        "Images": [
            "Use high-quality product images",
            "Ensure image URLs are valid and accessible",
            "Use HTTPS URLs for security",
            "Include product from multiple angles",
            "Maintain consistent image dimensions"
        ],
        "URLs & Links": [
            "Always use HTTPS protocol",
            "Ensure landing page links are valid",
            "Keep URLs short and descriptive",
            "Avoid tracking parameters when possible",
            "Test links regularly for broken URLs"
        ],
        "Categorization": [
            "Use consistent category hierarchy",
            "Align with platform requirements",
            "Use primary category for each product",
            "Keep category names standardized",
            "Avoid overly deep category nesting"
        ]
    }
    
    for category, tips in practices.items():
        with st.expander(f"📌 {category}", expanded=False):
            for i, tip in enumerate(tips, 1):
                st.write(f"{i}. {tip}")
    
    st.markdown("---")
    st.markdown("### 🎯 Optimization Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Quality:**")
        st.markdown("""
        - Maintain 95%+ data completeness
        - Regular audits and updates
        - Remove duplicate products
        - Fix formatting inconsistencies
        """)
    
    with col2:
        st.markdown("**Performance:**")
        st.markdown("""
        - Optimize feed file size
        - Use proper encoding (UTF-8)
        - Compress large feeds
        - Monitor feed update frequency
        """)

def about_page():
    """About page."""
    st.markdown("## ℹ️ About This Tool")
    
    st.markdown("""
    ### ChatGPT Product Feed Schema Validator
    
    A comprehensive tool for validating product feed schemas and improving data quality.
    
    **Features:**
    - ✓ Real-time schema validation
    - ✓ Comprehensive error detection
    - ✓ Smart recommendations
    - ✓ Multiple export formats
    - ✓ Detailed reporting
    - ✓ Best practices guidance
    
    **Supported Formats:**
    - JSON (native)
    - CSV (auto-conversion)
    - Direct text input
    - File upload
    
    **What We Validate:**
    - Required field presence
    - Data type compliance
    - Field length constraints
    - URL format validation
    - Price logic validation
    - Rating range validation
    - And more...
    
    **Export Options:**
    - Text Reports (.txt)
    - Comma-Separated Values (.csv)
    - JSON Results (.json)
    
    ---
    
    **Created with:**
    - Streamlit - Modern web app framework
    - Pandas - Data manipulation
    - Python - Core language
    
    **Version:** 1.0.0  
    **Last Updated:** 2026-01-06
    
    ---
    
    ### Support
    For issues, suggestions, or feedback, please contact the development team.
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Schema Fields", len(REQUIRED_FIELDS) + len(OPTIONAL_FIELDS))
    with col2:
        st.metric("Validation Rules", "25+")
    with col3:
        st.metric("Export Formats", 3)

if __name__ == "__main__":
    main()
